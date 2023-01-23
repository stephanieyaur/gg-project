import json
from Award import Award

def populate_awards_nominees(gg):
    f = open('gg2013answers.json')
    answersDictionary = json.load(f)
    for award_name in answersDictionary["award_data"]:
        newAward = Award()
        newAward.award_name = award_name
        award = answersDictionary["award_data"][award_name]
        for n in award["nominees"]:
            newAward.nominees.append(n)
        gg.awards.append(newAward)
    return gg