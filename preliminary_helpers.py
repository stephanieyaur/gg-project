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
        newAward.nominees.append(award["winner"])
        gg.awards.append(newAward)
    return gg

# Initialize winner dictionary for get_winners
# Returns a dictionary of actual awards as keys and empty string as values
def populate_awards():
    d = {}
    f = open('gg2013answers.json')
    answersDictionary = json.load(f)
    for award_name in answersDictionary["award_data"]:
        d[award_name] = 0
    return d