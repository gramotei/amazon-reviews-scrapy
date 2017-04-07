# amazon-reviews-scrapy
Download Amazon Reviews for specified product using Scrapy framework. Use it only for research purposes

# Installation
Create and enter your virtualenv with python3:
```
virtualenv -p python3 your_amazon_review_scrapy_env
source your_amazon_review_scrapy_env/bin/activate
```
Install dependencies
```
pip install -r requirements.txt
```

# Usage

To download reviews: 

```
scrapy crawl amazon-reviews-spider -a product_id=XXXXXXXX -o out.jl
```

where XXXXXXXX is Amazon product id like B002QQ8H8I


To export results to excel: 

```
python3.5 ./amazon_reviews_scrapy/export_to_excel.py out.jl out.jl.xlsx
```
