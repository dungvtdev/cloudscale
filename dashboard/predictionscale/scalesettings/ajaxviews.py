from django.http import JsonResponse
from . import utils
from horizon import exceptions
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from horizon import exceptions


def get_data_length(request, id):
    data_length = request.GET.get('data-length')
    try:
        data, ok = utils.get_data_length(request, data_length)
    except Exception:
        exceptions.handle(request,
                          _('Unable to retrieve data state length.'))
    return JsonResponse(data)


def run_containers(request, id):
    try:
        if request.method == 'POST':
            params = {}
            for k, v in request.POST.items():
                params[k] = v
            if 'csrfmiddlewaretoken' in params:
                del params['csrfmiddlewaretoken']

            is_ok = utils.run_group(request, id, params)
            if is_ok:
                return redirect(reverse("horizon:predictionscale:scalesettings:step3",
                                        kwargs={'id': id}))
            else:
                raise Exception("Can\'t up container. Try again")
        else:
            raise Exception('Can\'t do action.')
    except Exception as e:
        exceptions.handle(request, e.message)
        return redirect(reverse("horizon:predictionscale:scalesettings:step2",
                                kwargs={'id': id}))


def poll_process_data(request, id):
    data = utils.poll_process_data(request, id)
    return JsonResponse(data)

def get_last_predict(request, id):
    data = utils.get_last_predict(request, id)
    return JsonResponse(data)

def get_report_data(request, id):
    data = utils.get_report_data(request, id)
    return JsonResponse(data)