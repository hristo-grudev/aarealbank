import scrapy

from scrapy.loader import ItemLoader

from ..items import AarealbankItem
from itemloaders.processors import TakeFirst


class AarealbankSpider(scrapy.Spider):
	name = 'aarealbank'
	start_urls = ['https://www.aareal-bank.com/medienportal/newsroom/pressemitteilungen/archiv/2021']

	def parse(self, response):
		post_links = response.xpath('//ul[@class="clean press-entries"]/li')
		for post in post_links:
			url = post.xpath('./a/@href').get()
			date = post.xpath('./a/h6/time/text()').get()

			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//li[@class="nav-item"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@itemprop="articleBody" or @itemprop="description"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=AarealbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
