# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.website.utils import cleanup_page_name
from frappe.website.render import clear_cache
from frappe.modules import get_module_name

class WebsiteGenerator(Document):
	website = frappe._dict()

	def __init__(self, *args, **kwargs):
		self.route = None
		super(WebsiteGenerator, self).__init__(*args, **kwargs)

	def get_website_properties(self, key=None, default=None):
		out = getattr(self, '_website', None) or getattr(self, 'website', None) or {}
		if key:
			return out.get(key, default)
		else:
			return out

	def autoname(self):
		if not self.name and self.meta.autoname != "hash":
			self.name = self.scrubbed_title()

	def onload(self):
		self.get("__onload").update({
			"is_website_generator": True,
			"published": self.is_website_published()
		})

	def validate(self):
		if self.is_website_published() and not self.route:
			self.route = self.make_route()

		if self.route:
			self.route = self.route.strip('/.')[:139]

	def make_route(self):
		return self.scrubbed_title()

	def scrubbed_title(self):
		return self.scrub(self.get(self.get_website_properties('page_title_field', 'title')))

	def clear_cache(self):
		clear_cache(self.route)

	def scrub(self, text):
		return cleanup_page_name(text).replace('_', '-')

	def get_parents(self, context):
		'''Return breadcrumbs'''
		pass

	def on_trash(self):
		self.clear_cache()

	def is_website_published(self):
		"""Return true if published in website"""
		if self.get_website_properties('condition_field'):
			return self.get(self.get_website_properties('condition_field')) and True or False
		else:
			return True

	def get_page_info(self):
		route = frappe._dict()
		route.update({
			"doc": self,
			"page_or_generator": "Generator",
			"ref_doctype":self.doctype,
			"idx": self.idx,
			"docname": self.name,
			"controller": get_module_name(self.doctype, self.meta.module),
		})

		route.update(self.get_website_properties())

		if not route.page_title:
			route.page_title = self.get(self.get_website_properties('page_title'), 'title') \
				or self.get('name')

		return route
