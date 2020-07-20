import json

from django.http import HttpResponse


class NonHtmlDebugToolbarMiddleware:
	"""
	Обработчик запросов для debug_toolbar, позволяет отображать json response без запросов рендера.
	"""
	def __init__(self, get_response):
		self.get_response = get_response

	# One-time configuration and initialization.

	def __call__(self, request):
		# Code to be executed for each request before
		# the view (and later middleware) are called.

		response = self.get_response(request)

		if 'debug' in request.GET:
			if response['Content-Type'] == 'application/json':
				content = json.dumps(json.loads(response.content), sort_keys=True, indent=2)
				response = HttpResponse(u'<html><body><pre>{}</pre></body></html>'.format(content))

		return response
