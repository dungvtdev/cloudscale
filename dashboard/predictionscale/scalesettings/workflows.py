from django.utils.translation import ugettext_lazy as _
from horizon import workflows
from horizon import forms
from openstack_dashboard import api
from horizon import exceptions
from django.utils.text import normalize_newlines

from .utils import create_group, update_group
from openstack_dashboard.dashboards.predictionscale.backend.models \
    import GroupData
from openstack_dashboard.dashboards.predictionscale.backend \
    import client


class AddGroupInfoAction(workflows.Action):
    _group_id_regex = (r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
                       r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|[0-9]+|auto$')
    _group_id_help_text = _("Group ID should be UUID4 or integer. "
                            "Leave this field blank or use 'auto' to set "
                            "a random UUID4.")

    name = forms.RegexField(
        label=_("Name"),
        max_length=255,
        regex=r'^[\w\.\- ]+$',
        error_messages={'invalid': _('Name may only contain letters, numbers, '
                                     'underscores, periods and hyphens.')})
    group_id = forms.RegexField(label=_("ID"),
                                regex=_group_id_regex,
                                required=False,
                                initial='auto',
                                help_text=_group_id_help_text)
    desc = forms.CharField(max_length=512,
                           label=_("Desc"),
                           required=False)

    image = forms.ChoiceField(label='Image')
    flavor = forms.ChoiceField(label='Flavor')
    selfservice = forms.ChoiceField(label='Network')
    provider = forms.ChoiceField(label='Network Provider')

    script_data = forms.CharField(
        label=_('Script Data'),
        help_text="",
        widget=forms.widgets.Textarea(),
        required=False)

    def populate_image_choices(self, request, context):
        try:
            images, m, m = \
                api.glance.image_list_detailed(self.request)
        except Exception:
            images = []
            exceptions.handle(self.request, _("Unable to retrieve images."))
        return [(img.id, img.name) for img in images]

    def populate_flavor_choices(self, request, context):
        try:
            flavors, _, _ = api.nova.flavor_list_paged(request)
            # print(flavors)
        except Exception:
            flavors = []
            exceptions.handle(request,
                              _('Unable to retrieve flavor list.'))
        return [(f.id, f.name) for f in flavors]

    def populate_selfservice_choices(self, request, context):
        try:
            networks = api.neutron.network_list(request)
            return [(n.id, n.name) for n in networks
                    if not n.router__external and n.status == 'ACTIVE']
        except Exception:
            msg = _('Network list can not be retrieved.')
            exceptions.handle(self.request, msg)
            return []

    def populate_provider_choices(self, request, context):
        try:
            networks = api.neutron.network_list(request)
            return [(n.name, n.name) for n in networks
                    if n.router__external and n.status == 'ACTIVE']
        except Exception:
            msg = _('Network list can not be retrieved.')
            exceptions.handle(self.request, msg)
            return []

    def clean_name(self):
        name = self.cleaned_data.get('name').strip()
        if not name:
            msg = _('Group name cannot be empty.')
            self._errors['name'] = self.error_class([msg])
        return name

    def clean(self):
        cleaned_data = super(AddGroupInfoAction, self).clean()
        name = cleaned_data.get('name')
        group_id = cleaned_data.get('group_id')

        try:
            groups = client(self.request).get_groups()
        except Exception:
            groups = []
            msg = _('Unable to get groups list')
            exceptions.check_message(["Connection", "refused"], msg)
            raise

        if groups is not None and name is not None:
            for group in groups:
                if group.name.lower() == name.lower():
                    raise forms.ValidationError(
                        _('The name "%s" is already used by another group.')
                        % name
                    )
                if group.id == group_id:
                    raise forms.ValidationError(
                        _('The ID "%s" is already used by another group.')
                        % group_id
                    )

        cleaned_data['script_data'] = normalize_newlines(cleaned_data['script_data'])
        # files = self.request.FILES
        # script = self.clean_uploaded_files('script', files)
        #
        # if script is not None:
        #     cleaned_data['script_data'] = script

        return cleaned_data

    # def clean_uploaded_files(self, prefix, files):
    #     upload_str = prefix + "_upload"
    #
    #     has_upload = upload_str in files
    #     if has_upload:
    #         upload_file = files[upload_str]
    #         script = upload_file.read()
    #         if script != "":
    #             try:
    #                 normalize_newlines(script)
    #             except Exception as e:
    #                 msg = _('There was a problem parsing the'
    #                         ' %(prefix)s: %(error)s')
    #                 msg = msg % {'prefix': prefix,
    #                              'error': str(e)}
    #                 raise forms.ValidationError(msg)
    #             return script
    #
    #     return None

    class Meta(object):
        name = _("Group Information")
        help_text = _("Group define name, description, image, flavor")


class AddGroupInfo(workflows.Step):
    action_class = AddGroupInfoAction
    contributes = ("group_id",
                   "name",
                   "desc",
                   "image",
                   "flavor",
                   "selfservice",
                   "provider",
                   "script_data")


class UpdateGroupInstancesAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(UpdateGroupInstancesAction, self).__init__(request,
                                                         *args,
                                                         **kwargs)
        err_msg = _('Unable to retrieve instances list. '
                    'Please try again later.')
        context = args[0]
        group_id = context.get('group_id')

        default_role_field_name = self.get_default_role_field_name()
        self.fields[default_role_field_name] = forms.CharField(required=False)
        self.fields[default_role_field_name].initial = 'member'

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)

        # Get list of available projects.
        all_instances = []
        try:
            all_instances, hasmore = api.nova.server_list(self.request)
        except Exception:
            exceptions.handle(request, err_msg)

        groups = []
        try:
            groups = client(request).get_groups()
        except Exception:
            exceptions.handle(request, 'Can\'t retrieve group list. Try again')

        except_inst_ids = []
        for g in groups:
            if g.id == group_id:
                continue
            except_inst_ids = except_inst_ids + [id for id in g.instances]

        instances_list = [(inst.id, inst.name)
                          for inst in all_instances \
                          if inst.status == 'ACTIVE' and inst.id not in except_inst_ids]

        self.fields[field_name].choices = instances_list

        # If we have a POST from the CreateFlavor workflow, the flavor id
        # isn't an existing flavor. For the UpdateFlavor case, we don't care
        # about the access list for the current flavor anymore as we're about
        # to replace it.
        if request.method == 'POST':
            return

        # Get list of flavor projects if the flavor is not public.
        group_instances = []

        try:
            if group_id:
                group = client(request).get_group(group_id)
                group_instances = group.instances
        except Exception:
            exceptions.handle(request, err_msg)

        self.fields[field_name].initial = group_instances

    class Meta(object):
        name = _("Group Instances")
        slug = "update_group_instance"
        help_text = _("Group define instance added.")


class UpdateGroupInstances(workflows.UpdateMembersStep):
    action_class = UpdateGroupInstancesAction
    help_text = _("Select instances where group will apply and monitoring")
    available_list_title = _("All Instances")
    members_list_title = _("Selected Instances")
    no_available_text = _("No instances found.")
    no_members_text = _("No instances selected. ")
    show_roles = False
    depends_on = ("group_id",)
    contributes = ("instances",)

    def contribute(self, data, context):
        if data:
            member_field_name = self.get_member_field_name('member')
            context['instances'] = data.get(member_field_name, [])
        return context


class AddGroup(workflows.Workflow):
    slug = "add_group"
    name = _("Add Group")
    finalize_button_name = _("Add Group")
    success_message = _('Created new group "%s".')
    failure_message = _('Unable to create group "%s".')
    success_url = "horizon:predictionscale:scalesettings:index"
    default_steps = (AddGroupInfo, UpdateGroupInstances,)

    def format_status_message(self, message):
        return message % self.context['name']

    def handle(self, request, data):
        '''
        {'name': None, 'image': u'07b28db9-feae-4ea2-9ac2-024c4daae486', 
        'instances': [u'a7e600e2-6e7f-4460-a1b1-6e8dcd12baee'], 'flavor': u'1', 
        'group_id': u'auto', 'desc': u'tesst'}
        '''
        try:
            if not data['instances']:
                raise
        except:
            exceptions.handle(request, 'Instances must be assigned.')
            return False

        try:
            group = GroupData.create(data)
            ok = create_group(request, group)
            return ok
        except:
            msg = _('Can\'t create group. Try again later')
            exceptions.handle(request, msg)
            return False


class UpdateGroupInfoAction(AddGroupInfoAction):
    group_id = forms.CharField(widget=forms.widgets.HiddenInput)

    def clean(self):
        name = self.cleaned_data.get('name')
        group_id = int(self.cleaned_data.get('group_id'))
        try:
            groups = client(self.request).get_groups()
        except Exception:
            groups = []
            msg = _('Unable to get groups list')
            exceptions.check_message(["Connection", "refused"], msg)
            raise

        # Check if there is no group with the same name
        if groups is not None and name is not None:
            for group in groups:
                if (group.name.lower() == name.lower() and
                            group.id != group_id):
                    raise forms.ValidationError(
                        _('The name "%s" is already used by another '
                          'group.') % name)

        self.cleaned_data['script_data'] = \
            normalize_newlines(self.cleaned_data['script_data'])

        # files = self.request.FILES
        # script = self.clean_uploaded_files('script', files)
        #
        # if script is not None:
        #     self.cleaned_data['script_data'] = script

        return self.cleaned_data

    class Meta(object):
        name = _("Group Information")
        help_text = _("Group define name, description, image, flavor")



class UpdateGroupInfo(workflows.Step):
    action_class = UpdateGroupInfoAction
    depends_on = ("group_id",)
    contributes = ("name",
                   "desc",
                   "image",
                   "flavor",
                   "selfservice",
                   "provider",
                   "script_data")


class UpdateGroup(workflows.Workflow):
    slug = "update_group"
    name = _("Edit Group")
    finalize_button_name = _("Save")
    success_message = _('Modified group "%s".')
    failure_message = _('Unable to modify group "%s".')
    success_url = "horizon:predictionscale:scalesettings:index"
    default_steps = (UpdateGroupInfo,
                     UpdateGroupInstances)

    def format_status_message(self, message):
        return message % self.context['name']

    def handle(self, request, data):
        try:
            if not data['instances']:
                raise

        except:
            exceptions.handle(request, 'Instances must be assigned.')
            return False

        try:
            group = GroupData.create(data)
            id = group.group_id  # cai nay trick, la id chu khong phai group_id, duoc lay tu url
            ok = update_group(request, group, id)
            return ok
        except:
            msg = _('Can\'t create group. Try again later')
            exceptions.handle(request, msg)
            return False
