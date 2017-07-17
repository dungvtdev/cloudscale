# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from horizon import tables
from horizon import forms
from horizon import workflows
from openstack_dashboard.dashboards.predictionscale.scalesettings \
    import tables as settings_tables
from openstack_dashboard.dashboards.predictionscale.scalesettings \
    import workflows as settings_workflows

from openstack_dashboard.dashboards.predictionscale.backend \
    import client
from openstack_dashboard.dashboards.predictionscale.backend.models import GroupData
from horizon import views
from horizon import exceptions
from django.views.generic.base import RedirectView
from openstack_dashboard import api

INDEX_URL = "horizon:predictionscale:scalesettings:index"


def get_group_view_data(request, groups):
    try:
        flavors = api.nova.flavor_list(request)
    except Exception:
        flavors = []
        exceptions.handle(request, ignore=True)

    try:
        images, more, prev = api.glance.image_list_detailed(request)
    except Exception:
        images = []
        exceptions.handle(request, ignore=True)

    try:
        instances, has_more = api.nova.server_list(request)
    except Exception:
        instances = []
        exceptions.handle(request, ignore=True)

    result = []
    for group in groups:
        group = group.clone()

        if group.flavor and flavors:
            flavor_name = next((f.name for f in flavors if f.id == group.flavor), None)
            group.flavor = flavor_name or group.flavor

        if group.image and images:
            image_name = next((img.name for img in images if img.id == group.image), None)
            group.image = image_name or group.image

        if group.instances and instances:
            inst_names = []
            for inst_id in group.instances:
                name = next((inst.name for inst in instances if inst.id == inst_id), None)
                inst_names.append(name or inst_id)

            group.instances = inst_names

        result.append(group)

    return result


class InstanceTmpl:
    name = None
    id = None

    def __init__(self, name, id):
        self.name = name
        self.id = id


class AddView(workflows.WorkflowView):
    workflow_class = settings_workflows.AddGroup
    # dung lai template mac dinh
    template_name = 'admin/flavors/create.html'
    page_title = _("Add Group")


class UpdateView(workflows.WorkflowView):
    workflow_class = settings_workflows.UpdateGroup
    template_name = 'admin/flavors/create.html'
    page_title = _("Update Group")

    def get_initial(self):
        group_id = self.kwargs['id']

        try:
            # Get initial group information
            group = client(self.request).get_group(group_id)
        except Exception:
            group = None
            exceptions.handle(self.request,
                              _('Unable to retrieve flavor details.'),
                              redirect=reverse_lazy(INDEX_URL))
        if group is not None:
            group = get_group_view_data(self.request, [group, ])[0]
            return group.to_dict()
        else:
            return GroupData().to_dict()
        # return {'flavor_id': flavor.id,
        #         'name': flavor.name,
        #         'vcpus': flavor.vcpus,
        #         'memory_mb': flavor.ram,
        #         'disk_gb': flavor.disk,
        #         'swap_mb': flavor.swap or 0,
        #         'rxtx_factor': flavor.rxtx_factor or 1,
        #         'eph_gb': getattr(flavor, 'OS-FLV-EXT-DATA:ephemeral', None)}


class IndexView(RedirectView):
    permanent = False
    url = reverse_lazy('horizon:predictionscale:scalesettings:step1')


class Step1View(tables.DataTableView):
    table_class = settings_tables.ScaleGroupTable
    template_name = 'predictionscale/scalesettings/group_table.html'
    page_title = _('Settings')
    step_title = _('Group Settings')
    step_index = 1

    def get_data(self):
        try:
            groups = client(self.request).get_groups()
            if not groups:
                return []
            groups = get_group_view_data(self.request, groups)
            for group in groups:
                if group.instances is not None:
                    group.instances = '\n'.join(group.instances)
            return groups
        except Exception:
            err_msg = _('Can\'t retrieve group list')
            exceptions.handle(self.request, err_msg)
            return []

    def get_context_data(self, **kwargs):
        context = super(Step1View, self).get_context_data(**kwargs)
        context['step_title'] = self.step_title
        context['step_index'] = self.step_index
        return context


def get_group_context(view, request, context, *args, **kwargs):
    id = kwargs['id']
    context['step_title'] = view.step_title
    context['step_index'] = view.step_index

    try:
        group = client(request).get_group(id)
        group = get_group_view_data(request, [group, ])[0]
        if group is None:
            raise
    except:
        err_msg = _('Can\'t retrieve group')
        exceptions.handle(request, err_msg)
        return context

    # instances = group.instances
    insts = zip(group.instances, group.instances_id)
    context['instances'] = [InstanceTmpl(inst[0], inst[1]) for inst in insts]
    context['group'] = group
    return context


class Step2View(views.APIView):
    template_name = 'predictionscale/scalesettings/service_setting.html'
    step_title = _('Service Settings')
    step_index = 2

    def get_data(self, request, context, *args, **kwargs):
        context = super(Step2View, self).get_context_data(**kwargs)
        return get_group_context(self, request, context, *args, **kwargs)


class Step3View(views.APIView):
    template_name = 'predictionscale/scalesettings/group_control.html'
    step_title = _('Group Control')
    step_index = 3

    # def get_data(self, request, context, *args, **kwargs):
    #     context = super(Step3View, self).get_context_data(**kwargs)
    #     context['step_title'] = self.step_title
    #     context['step_index'] = self.step_index
    #     return context
    def get_data(self, request, context, *args, **kwargs):
        context = super(Step3View, self).get_context_data(**kwargs)
        return get_group_context(self, request, context, *args, **kwargs)

        # class IndexView(views.APIView):
        #     # A very simple class-based view...
        #     template_name = 'predictionscale/scalesettings/index.html'

        #     def get_data(self, request, context, *args, **kwargs):
        #         # Add data to the context here...
        #         return context


class ReportView(views.APIView):
    template_name = 'predictionscale/scalesettings/report.html'

    def get_data(self, request, context, *args, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        id = kwargs['id']
        name = 'test'
        context['inst'] = {
            'id': id,
            'name': name,
        }
        return context