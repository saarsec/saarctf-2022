from datetime import datetime
from string import printable
from bytewarden.settings import INTERNAL_APPS

IS_PRINTABLE = lambda chars: all(c in printable for c in chars)
IS_INTERNAL  = lambda req: any(app_name in req.path for app_name in INTERNAL_APPS)

def RequestsMiddleware(get_response):

	def filter_dict(req_dict, is_internal = False):

		new_dict = {}
		for k, v_list in req_dict.lists():
			k = "".join(filter(IS_PRINTABLE, k))
			k = k.lower()
			v_list = list(filter(IS_PRINTABLE, v_list))
			if not v_list:
				continue

			if v_list[0].isdigit() and len(v_list[0]) < 3:
				if not is_internal:
					new_dict[k] = list(v_list[0])
				else:
					new_dict[k] = v_list
			else:
				new_dict[k] = v_list[0]

		return new_dict

	def middleware(request):

		request.path = request.path.lower()
		request.path = request.path.replace("../", "")

		request.COOKIES["date"] = datetime.now()

		if request.method == "GET":
			request.GET  = filter_dict(request.GET, IS_INTERNAL(request))
		else:
			request.POST = filter_dict(request.POST, IS_INTERNAL(request))

		response = get_response(request)
		return response

	return middleware

