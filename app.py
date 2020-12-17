#!/venv/scripts python3

from flask import Flask, render_template, request, session, Markup, flash, redirect, url_for
from random import randint, sample, choice
from requests import get
from bs4 import BeautifulSoup

app = Flask(__name__)

app.secret_key = "eriguaoh4iu5h3095873tg4w5tr340546549584894"

MIN_WIDTH = 400
LEVEL_UP = 12
NEXT_STAGE = 7
COUNTRY_START = 10
WRONG_ANSWER_STREAK = 2 # give MC question if this many wrong in a row

ERRORS = """.tif
CentralAutoLogin""".split("\n")

WELL_DONE = """Yeah! You got it!    
That's right..
Well done!
Correct!
PERFECT!
How did you know?!
Awesome!
YEAHHHH!
That was right...
Brill!
Superb!
You are super cultured!!
Christopher Columbus <3!
Wow - so well travelled!
Culture vulture!
Amazing!
Wooohooo!
Yeah! You did it!
W00T W00T
That was it.
That's the one!
Nailed it!
Smashed it!
Globetrotter!
World citizen!
Adventurer!
You got the smarts!
Absolutely correct.
10/10
5 gold stars!
Superduper!
Wunderbar!
Geng mahk!
Delicioso!
Nice one m8!
Great answer buddy!
You da man!""".split("\n")

INCORRECT = """Errr... no?
That wasn't correct.
Wrong!
Nope...
Wrong answer.
Sorry - that was wrong...
No, you didn't get that one right.
WRONG!
Ooops...
Are you sure you're good at this?
What now?
R U SURE?
What was that?
Erm.. no
No way hozay.
Nein.
Hell no.
Absolutely not.
100% wrong.
Not at all.
Really?
No.
Incorrect.
Not correct.""".split("\n")
"https://commons.wikimedia.org/w/index.php?sort=relevance&search=%22{}+{}%22&title=Special:Search&profile=advanced&fulltext=1&advancedSearch-current=%7B%7D&ns0=1&ns6=1&ns12=1&ns14=1&ns100=1&ns106=1"

URLS = ["https://www.google.com/search?tbm=isch&q={}+{}"]

COUNTRIES = """chinese
indian
american
indonesian
pakistani
brazilian
nigerian
bangladeshi
russian
mexican
japanese
ethiopian
filipino
egyptian
vietnamese
congolese
turkish
iranian
german
thai
british
french
italian
tanzanian
south african
burmese
kenyan
south korean
colombian
spanish
ugandan
argentine
algerian
sudanese
ukrainian
iraqi
afghan
polish
canadian
moroccan
saudi
uzbek
peruvian
angolan
malaysian
mozambican
ghanaian
yemeni
nepalese
venezuelan
malagasy
cameroonian
ivorian
north korean
australian
nigerien
taiwanese
sri lankan
burkinabé
malian
romanian
malawian
chilean
kazakh
zambian
guatemalan
ecuadorian
syrian
dutch
senegalese
cambodian
chadian
somali
zimbabwean
guinean
rwandan
beninese
burundian
tunisian
bolivian
belgian
haitian
cuban
south sudanese
dominican
czech
greek
jordanian
portuguese
azerbaijani
swedish
honduran
emirati
hungarian
tajikistani
belarusian
austrian
papuan
serbian
israeli
swiss
togolese
sierra leonean
cantonese
lao
paraguayan
bulgarian
libyan
lebanese
nicaraguan
kyrgyzstani
salvadoran
turkmen
singaporean
danish
finnish
congolese
slovak
norwegian
omani
palestinian
costa rican
liberian
irish
central african
new zealander
mauritanian
panamanian
kuwaiti
croatian
moldovan
georgian
eritrean
uruguayan
bosnian
herzegovinian
mongolian
armenian
jamaican
qatari
albanian
puerto rican
lithuanian
namibian
gambian
botswanan
gabonese
basotho
macedonian
slovenian
bissau-guinean
latvian
bahraini
equatorial guinean
trinidadian
tobagonian
estonian
timorese
mauritian
cypriot
swazi
djiboutian
fijian
réunionese
comoran
guyanese
bhutanese
solomon islander
macanese
montenegrin
luxembourgish
sahrawi
surinamese""".split("\n")

def parse_wikimedia(url):

    url = url.replace("/thumb", "")
    url = url.split("/")
    return "/".join(url[:-1])


THINGS = ["man", "woman", "food","man+walking", "money", "woman+walking", "city","man+dancing", "nature", "woman+dancing", "politician", "man+driving", "celebration", "woman+driving", "building"]


def get_random_image():
    error = True
    while error:
        try:
            countries = COUNTRIES[:COUNTRY_START+1 + (5 * session['level'])]
            print(countries)

            if randint(0, 1):
                options = sample(countries, 4)
                nationality = choice(options)
            else:
                options = []
                nationality = choice(countries)

            upper = session['stage'] + 1

            thing = choice(THINGS[0:upper])
            print(thing)

            url = choice(URLS).format(nationality, thing)

            source = get(url).content

            # try:
            if "wikimedia" in url:
                sources = [s for s in BeautifulSoup(source).findAll('img')]
                sources = [parse_wikimedia(s['src']) for s in sources]
                sources = sources[:20]

            elif "google" in url:
                sources = [s['src'] for s in BeautifulSoup(source).findAll('img') if s.get('src') is not None]
                sources = sources[5:20]

            else:
                sources = [s['srcset'].split(", ") for s in BeautifulSoup(source).findAll('img') if
                           s.get('srcset') is not None]

                sources = [list_[3] for list_ in sources[1:20:2]]
            if len(sources) == 0:
                raise Exception("no data")
            else:
                source = choice(sources)

                for error_sig in ERRORS:
                    if error_sig in source or source=="":
                        raise Exception("Dodgy url")
                error = False
        except Exception as e:
            print(e)
            pass

    return {'options':options,
            'nationality':nationality,
            'url':url,
            'source':source}


def preload(process_redirect=True):

    session['preload'] = [get_random_image() for i in range(5)]
    print(session['preload'])
    if process_redirect:
        return redirect(url_for("game"))

@app.route("/")
def home():
    session['scores'] = []
    session['stage'] = 1
    session['level'] = 1

    for msg in ["Look at the picture.", "Guess the nationality - starting with the TOP {} most common nationalities in the world.".format(COUNTRY_START), "Press BEGIN when ready..."]:
        flash(msg, "green")
    return render_template("game.html", start=True, stage=1, level=1, score="?", guesses=0)

@app.route("/game", methods=["GET", "POST"])
def game():
    error = ""
    img_src = ""
    guess = ""



    if request.method == "GET":

        try:
            session['next'] = session['preload'].pop(0)
        except:
            return preload()

        feedback = False

        image_data = session['next']

        img_src = image_data['source']

        options = image_data['options']

        if options is None and sum(session['scores'][0 - WRONG_ANSWER_STREAK:]) == 0:
            return redirect(url_for('game'))

        session['img_src'] = img_src
        session['answer'] = image_data['nationality']
        # except Exception as e:
        #
        #
        #
        #     error = Markup("""<p> ERROR {}</p>
        #     <p>gender: {}</p>
        #     <p>nationality: {}</p>
        #     <p>url: {}</p>
        #
        #
        #     """.format(e, gender, nationality, url))


    else:

        print("post request")
        guess = request.form.get('guess')
        answer = session['answer']
        feedback = True
        scores = session.get('scores')
        if guess.strip().lower() == answer.lower():
            mark = 1
            flash(choice(WELL_DONE), "green")

        else:
            mark = 0
            flash("{} Correct answer: {}".format(choice(INCORRECT), answer), "red")

        session['scores'].append(mark)


        if mark:
            if sum(scores) % NEXT_STAGE == 0:
                session['stage'] += 1
                flash("NEXT STAGE!", "green")
                flash(Markup("You've unlocked: <b>{}</b>".format(THINGS[session['stage']])), "green small")
            elif sum(scores) % LEVEL_UP == 0:
                session['level'] += 1
                flash("LEVEL UP!", "green")
                flash(Markup("The next <b>five most common nationalities</b> have been added:"), "small green")
                max_ = (session['level'] * 5) + COUNTRY_START
                min_ = max_ - 5
                flash(", ".join(COUNTRIES[min_:max_]), "small green")

        options = []

        img_src = session['img_src']

    scores = session.get('scores')

    if len(scores) > 0:
        score = int(round((sum(scores) / len(scores)) * 100, 0))
        rag_rating = "rating{}".format(int(score / 20))
    else:
        score = "tbc"
        rag_rating = ""

    if error:
        feedback = True



    return render_template("game.html", feedback=feedback, error=error, options=options, guess=guess, score=score, rag_rating=rag_rating, img_src=img_src, guesses=len(scores), stage=session['stage'], level=session['level'])




if __name__ == "__main__":

    app.run()