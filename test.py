import json

result = json.dumps({"status":"success","data":{"url":"https://www.rishabh.xyz/","insights":{"technologies":[{"name":"Ruby on Rails","confidence":100,"logo":"https://www.wappalyzer.com/images/icons/Ruby%20on%20Rails.png","url":"https://rubyonrails.org","categories":["Web frameworks"]},{"name":"Varnish","confidence":100,"logo":"https://www.wappalyzer.com/images/icons/Varnish.svg","url":"http://www.varnish-cache.org","categories":["Caching"]},{"name":"Fastly","confidence":100,"logo":"https://www.wappalyzer.com/images/icons/Fastly.svg","url":"https://www.fastly.com","categories":["CDN"]},{"name":"Cloudflare","confidence":100,"logo":"https://www.wappalyzer.com/images/icons/CloudFlare.svg","url":"http://www.cloudflare.com","categories":["CDN"]},{"name":"GitHub Pages","confidence":100,"logo":"https://www.wappalyzer.com/images/icons/GitHub.svg","url":"https://pages.github.com/","categories":["PaaS"]}],"lighthouse":"null"}}})

result = json.loads(result)

tech_list = result['data']['insights']['technologies']
len_tech = len(tech_list)
string = ""
if len_tech > 1:
    for n, tech in enumerate(tech_list):
        if n < len_tech - 1:
            string += "├ " + str(tech['name']) + ' - ' + str(tech['categories'][0]) + "\n"
        else:
            string += "└ " + str(tech['name']) + ' - ' + str(tech['categories'][0])
else:
    string += "└ " + tech_list[0]

print("Detected {} technologies behind the site:".format(len_tech))
print(string)