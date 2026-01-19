import collections
import pprint
import sys
import textwrap

import secretagent as secret

CONFIG = dict(
    service="anthropic", model="claude-haiku-4-5-20251001",
    echo_call=True, echo_service=True)

def fake_common_concerns(q1, q2):
    return "they are similar lengths" if 0.9 < (len(q1) / len(q2)) < 1.1 else "no common concerns"

@secret.subagent()
def strong_common_concerns(q1: str, s2:str) -> str:
    """Given two questions about a paper, identify any strong and
    obvious common concerns expressed by the two questions.  If there
    are no strong and obvious commonalities, then return the string
    'no common concerns'.

    Examples:
    >>> strong_common_concerns("Many medical errors stem from human limitations such as fatigue and imperfect judgment. What role can AI play in reducing these errors in tasks like diagnosis, treatment decisions, and risk evaluation? If the potential is significant, why do we still see relatively limited use of AI in everyday medical practice?", "With reference to “Intelligence Augmentation” described in the article, what should the true goal of AI systems be: replacing human decision-making or augmenting it?")
    "Strong commonality: Both questions raise issues about the potential for AI to augment or replace human decision-making"

    >>> strong_common_concerns("how should we incorporate the perspectives of social sciences and humanities into the development of AI?", "How can we facilitate AI being treated as an engineering discipline when money is being poured into superintelligence ideas?")
    "no common concerns"

    >>> strong_common_concerns("How would the author would feel differently today about the progress in human-imitative AI? Would the progress in robotics be significant to change the author's opinion or are we still limited by the slow rise in accountability, interpretability and fairness?", "This article is from 2019, and obviously predates LLMs. Do we think LLMs have helped or have the potential to solve IA or II system problems?")
    "Strong commonality: Both questions note that the paper discussed is several years old, and that recent advances in robotics and LLMs might have since changed the author's opinions, as expressed in the paper."

    """

if __name__ == '__main__':

    secret.configure(**CONFIG)

    filename = sys.argv[1]
    with open(filename, 'r') as fp:
        questions = fp.readlines()

    already_grouped = set()
    groups = collections.defaultdict(list)
    for i, qi in enumerate(questions):
        for j, qj in enumerate(questions[i+1:]):
            if j in already_grouped or j == i:
                continue
            if strong_common_concerns(qi, qj) != "no common concerns":
                print(f'{i}, {j} are similar')
                groups[i].append(j)
                already_grouped.add(j)

    def prwrapq(i):
        print(i, '\n'.join(textwrap.wrap(questions[i])))

    for i,js in groups.items():
        print('=' * 60)
        prwrapq(i)
        for j in js:
            print()
            prwrapq(j)            
