from openerp import models, fields, api
from openerp.osv import orm
from openerp.tools.translate import _

from bs4 import BeautifulSoup
from lxml import etree
from io import StringIO, BytesIO
import requests
import lxml
import time

class pag_wolftrak(models.Model):
	_name = 'pag.wolftrak.search'
	_description = "Paginas Amarillas Buscador"

	busc 	 = fields.Char(string='Busqueda')
	fh_busc  = fields.Date(string='Fecha de Busqueda', default=time.strftime('%Y-%m-%d'))
	pag_line = fields.Many2many('pag.wolftrak.line', 'empresa', 'tlf')

	@api.onchange('busc')
	def searching(self):

		keyword = self.busc
		if type(keyword) != bool:
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
				if span.parent.name == 'a' and span.attrs and span.attrs != {'class': ['search-cat']} and span.attrs != {'itemprop': 'streetAddress'} and span.attrs != {'itemprop': 'addressLocality'} and span.string != ', ':
					sdata = sdata+span.string+',,'
					data.append(span.string)

			meta=[]
			for n in range(len(data)):
				if n%2 == 0:
					meta.append(data[n:n+2])

			emplist = []
			tlflist = []
			for n in meta:
				emplist.append(n[0])
				tlflist.append(n[1])
			# funciona...
			mayorlist = []
			for n in emplist:
				result={}
				result.update({'srch_id':n})
				mayorlist.append(result)
			self.pag_line = mayorlist
			i = 0
			for m in self.pag_line:
				m.empresa = emplist[i]
				m.tlf = tlflist[i]
				i += 1
			emplist = []
			tlflist = []
		else:
			self.empresa = ''
			self.tlf = ''

class pag_line(models.Model):
	_name = 'pag.wolftrak.line'

	srch_id	= fields.Many2one('pag.wolftrak.search') 
	empresa = fields.Char(string="Empresa")
	tlf 	= fields.Char(string="Telefono")
