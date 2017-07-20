from horizon import tables
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from django.utils.translation import npgettext_lazy
from django.core.urlresolvers import reverse

from .utils import drop_group
from horizon import exceptions
from horizon.utils import filters


class DeleteGroup(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Group",
            u"Delete Groups",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Group",
            u"Deleted Groups",
            count
        )

    def delete(self, request, obj_id):
        try:
            return drop_group(request, obj_id)
        # print('*************************** delete *********************')
        # print('is ok %s ' % ok)
        except Exception:
            msg = _('Can\'t delete group. Try again later.')
            exceptions.handle(request, msg)


class AddGroup(tables.LinkAction):
    name = 'add_group'
    verbose_name = _('Add Group')
    url = "horizon:predictionscale:scalesettings:add_group"
    classes = ("ajax-modal",)
    icon = "plus"

    def allowed(self, request, datum=None):
        return True


class UpdateGroup(tables.LinkAction):
    name = "update_group"
    verbose_name = _("Edit Group")
    url = "horizon:predictionscale:scalesettings:update"
    classes = ("ajax-modal",)
    icon = "pencil"


# class GroupControl(tables.LinkAction):
#     name = "control"
#     verbose_name = _("Group Control")
#     url = "horizon:predictionscale:scalesettings:step3"
#
#     # icon = "pencil"
#
#     def get_link_url(self, group):
#         url = reverse(self.url, args=[group.id])
#         return url
#
#     def allowed(self, request, group):
#         can = (group is not None and group.enable)
#         return can


class ScaleGroupTable(tables.DataTable):
    # name = tables.WrappingColumn("name",
    #                              link="horizon:project:instances:detail",
    #                              verbose_name=_("Group Name"))
    name = tables.Column("name",
                         link="horizon:predictionscale:scalesettings:step2",
                         verbose_name=_("Group Name"))
    # group_id = tables.Column("group_id", verbose_name=_("ID"))

    desc = tables.Column("desc",
                         verbose_name=_("Descriptions"))

    instances = tables.Column("instances",
                              verbose_name=_("Instances"))

    image = tables.Column("image",
                          verbose_name=_("Image"))
    flavor = tables.Column("flavor",
                           verbose_name=_("Flavor"))
    created = tables.Column("created",
                            verbose_name=_("Time since created"),
                            filters=(filters.parse_isotime,
                                     filters.timesince_sortable),
                            attrs={'data-type': 'timesince'})
    proxy_url = tables.Column("proxy_url",
                              verbose_name=_("URL"))
    process = tables.Column("process",
                            verbose_name=_("Process"))
    number_vm = tables.Column("number_vm",
                              verbose_name=_("Number VMs"))

    class Meta(object):
        name = 'scalegroups'
        verbose_name = _("Scale Groups")
        table_actions = (AddGroup, DeleteGroup,)
        row_actions = (UpdateGroup, DeleteGroup,)
