import fire

header = """
<html>
<head>
<title>Quantum Weirdness for ML Researchers: Chapter {n}</title>
<!--- mathjax  and pic --->
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-mml-chtml.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head>

<body>
<main class="container">
<header><h1>{title}</h1></header>
<section>
"""

footer = """
</section></main></body></html>
"""


def stub(chap_num: int, chap_title: str):
    print(header.format(n=chap_num, title=chap_title))
    print('blah blah')
    print(footer)

if __name__ == "__main__":
    fire.Fire()

