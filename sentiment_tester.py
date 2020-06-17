from sentiment import *

keyword = "GitHub"
start_date = "2020-01-01"
end_date = "2020-01-04"

tsentiments = TwitterSentiments()

tsentiments.search(keyword, start_date, end_date, result_path = "output/sentiment")