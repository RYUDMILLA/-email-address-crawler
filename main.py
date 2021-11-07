import selenium.common.exceptions
import time
import crawler as cr
import csv

def initialize_csv(file):
    f = open(file, 'w+')
    writer = csv.writer(f)
    # writer.writerow(['center', 'emails', 'maps'])
    f.close()

in_file = "centers.csv"
out_file = "results.csv"
error_file = "errors.csv"
unmatched_file = "not_matched.csv"


in_csv = open(in_file, 'rt', encoding='UTF8')

initialize_csv(out_file)
initialize_csv(unmatched_file)
initialize_csv(error_file)


crawler = cr.crawler()

for center in in_csv:
    try:
        info = crawler.extract_links(center)
        if info['links']:
            info2 = crawler.extract_emails(info['links'])
            info.update(info2)
            crawler.save_to_file(info, out_file, unmatched_file)
    except(selenium.common.exceptions.StaleElementReferenceException):
        print(f"\n{center} Staleerror\n")
        crawler.record_error(error_file, center)
        continue
    except:
        print(f"\n{center} Noneerror\n")
        crawler.record_error(error_file, center)
        continue

crawler.kill()
