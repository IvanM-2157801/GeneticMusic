import base64

strudel_script = """
setcpm(160/5)

$: note("[1 ~] [2 ~] 3 4")
  .scale("c:major").gain(.05)


$: note("1 2 3 4 1 2 3 4")
  .scale("c:").gain(.05)
"""

encoded_script = base64.b64encode(strudel_script.encode('utf-8')).decode('utf-8')
print(f"https://strudel.cc/#{encoded_script}")