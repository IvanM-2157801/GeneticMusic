import base64

def create_strudel(notes: list[str], total_notes: int, bpm: int):
	strudel_script = f"""
setcpm({bpm}/{total_notes})

$: note("{" ".join(notes)}")
.scale("c:major").gain(0.2).sound("piano")
"""

	encoded_script = base64.b64encode(strudel_script.encode('utf-8')).decode('utf-8')
	print(f"https://strudel.cc/#{encoded_script}")