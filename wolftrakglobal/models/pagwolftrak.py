from openerp import models, fields, api
from openerp.osv import orm
from openerp.tools.translate import _

from bs4 import BeautifulSoup
from lxml import etree
from io import StringIO, BytesIO
import requests
import lxml

class pag_wolftrak(models.Model):
	_name = 'pag.wolftrak'

	empresa = fields.Char(string="Empresa", compute="searching")
	tlf = fields.Char(string="Telefono", compute="searching")
	busc = fields.Char(string="Busqueda: ")

	@api.onchange('busc')
	@api.multi
	def searching(self):

		keyword = self.busc
		keyword = keyword.replace(' ','-')

		page = requests.get('http://www.paginasamarillas.com.do/Searchpg.aspx?nombre='+keyword+'&ciudad=Santo+Domingo&showQuantity=100&order=Relevancia&currentPage=1&classCode=&subClassCode=&keyword=&other=&latitude=&longitude=&filter=true')
		content = page.content

		soup = BeautifulSoup(content, 'lxml')
		s_body = soup.body

		s_body_span = s_body.find_all('span')
		data = [] 
		sdata = '' 
		i=0
		for span in s_body_span:
			if span.parent.name == 'a' and span.attrs and span.attrs != {'class': ['search-cat']} and span.attrs != {'itemprop': 'streetAddress'} and span.attrs != {'itemprop': 'addressLocality'}:
				sdata = sdata+span.string+',,'
				data.append(span.string)

		meta=[]
		for n in range(len(data)):
			if n%2 == 0:
				meta.append(data[n:n+2])

		emp = []
		i=0
		for n in meta:
			emp.append(n[i][0])
			i=i+1
		# funciona...
		self.empresa = emp
		self.tlf = meta

		# 		self.empresa = x[0]
		# 		self.tlf = x[1]
				# raise orm.except_orm(_("Warning"),_(empresa+tlf+"""<br> Generando... """),)

		# for x in self:
		# 	x.empresa = "empresaaa..."
		# 	x.tlf = "tlf...."