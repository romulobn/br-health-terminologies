import scrapy
import re

class IcdSpider(scrapy.Spider):
    name='icd'
    start_urls=['http://cid.ninsaude.com']

    def parse(self, response):
        for box_chapter in response.css('div.boxChapter'):
            yield response.follow(box_chapter.css('a::attr(href)').extract_first(), callback=self.parse_group)

        
    def parse_group(self, response):
        for chapter_group in response.css('div.boxGroupl'):
            yield response.follow(chapter_group.css('h3>a::attr(href)').extract_first(), callback=self.parse_codes)

    def parse_codes(self, response):
        for code_href in response.css('table.a>tbody>tr>td>a'):
            yield response.follow(code_href.css('::attr(href)').extract_first(), callback=self.parse_code)

    def parse_code(self, response):
        code = response.css('#tbCid>tbody>tr:nth-child(1)>td:nth-child(2)::text').extract_first().strip()
        code = re.sub(r'[\.\-\;\*\+]', '', code)

        description = response.css('#tbCid>tbody>tr:nth-child(2)>td:nth-child(2)::text').extract_first().strip()
        
        classification = response.css('#tbCid>tbody>tr:nth-child(3)>td:nth-child(2)::text').extract_first().strip()
        if (classification == u'N\xe3o tem dupla classifica\xe7\xe3o'):
            classification = None
        if (classification == u'Classifica\xe7\xe3o por manifesta\xe7\xe3o'):
            classification = '*'
        if (classification == u'Classifica\xe7\xe3o por etiologia'):
            classification = '+'

        gender_restriction = response.css('#tbCid>tbody>tr:nth-child(4)>td:nth-child(2)::text').extract_first().strip()
        if (gender_restriction == u'Pode ser utilizada em qualquer situa\xe7\xe3o'):
            gender_restriction = None
        if (gender_restriction == u'S\xf3 deve ser utilizada para o sexo feminino'):
            gender_restriction = 'F'
        if (gender_restriction == u'S\xf3 deve ser utilizada para o sexo masculino'):
            gender_restriction = 'M'
        
        death_cause = response.css('#tbCid>tbody>tr:nth-child(5)>td:nth-child(2)::text').extract_first().strip()
        death_cause = 'Yes' if death_cause != u'N\xe3o h\xe1 restri\xe7\xe3o' else 'No'
        
        reference = response.css('#tbCid>tbody>tr:nth-child(6)>td:nth-child(2)::text').extract_first().strip()
        reference = reference if reference !=  u'N\xe3o h\xe1' else None

        group_name = response.css('div.line5 div.content50l>h2::text').extract_first().strip()
        group_name = re.search(r'Grupo entre (.+) e (.+)', group_name)
        group_name = "%s-%s" % (group_name.group(1).strip(), group_name.group(2).strip())
        
        group_description = response.css('div.line5 div.content50l>p ::text').extract_first().strip()

        chapter_name = response.css('div.line5 div.content50>h2::text').extract_first().strip()
        chapter_description = response.css('div.line5 div.content50>p::text').extract_first().strip()


        yield {
            'code': code,
            'description': description,
            'classification': classification,
            'gender_restriction': gender_restriction,
            'death_cause': death_cause,
            'reference': reference,
            'group_name': group_name,
            'group_description': group_description,
            'chapter_name': chapter_name,
            'chapter_description': chapter_description
        }