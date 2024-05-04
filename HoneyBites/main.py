import os
from flask import Flask, redirect, url_for, render_template, request, session, make_response
from database import HoneyBitesDB
import open_ai_categorize as oa
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "b747c1eff28e1ca5d0c0f563a1018627363fc18406d080ec1a54d4bb7a4361af"
app.permanent_session_lifetime = timedelta(minutes=60)

@app.route("/")
def home():
    template = render_template("home.html")
    response = make_response(template)
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
    return response

@app.route("/signup", methods=["POST", "GET"])
def signup():
    # if "user" in session:
    #     return redirect(url_for("user"))
    if request.method == "POST":
        name = request.form["Name"]
        username = request.form["Username"]
        email = request.form["Email"]
        password = request.form["Password"]
        gender = request.form["Gender"]
        sexuality = request.form["Sexuality"]
        age = request.form["Age"]
        city = request.form["City"]
        bio = request.form["Bio"]

        info_dict = {"name": name,
                     "username": username,
                     "email": email,
                      "password": password,
                      "gender": gender,
                      "sexuality": sexuality,
                      "age": age,
                      "city": city,
                      "cuisine_preference": [],
                      "bio": bio}
        
        # session["Username"] = username
        # session["Password"] = password

        HoneyBitesDB.create_new_user(info_dict)

        # Session stuff
        session.permanent == True
        username = request.form["Username"]
        password = request.form["Password"]
        session["Username"] = username
        session["Password"] = password

        template = redirect(url_for("foodadd"))
        response = make_response(template)
        response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
        return response
    
    else:
        template = render_template("signup.html")
        response = make_response(template)
        response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
        return response

@app.route("/foodadd", methods=["POST", "GET"])
def foodadd():
    if not "Username" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        food = request.form["food"]
        HoneyBitesDB.add_user_preference(session["Username"], food)


    template = render_template("foodadd.html")
    response = make_response(template)
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
    return response

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]
        
        session.permanent == True
        username = request.form["Username"]
        password = request.form["Password"]
        session["Username"] = username
        session["Password"] = password

        return redirect(url_for("foodadd"))

    template = render_template("login.html")
    response = make_response(template)
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
    return response

@app.route("/logoff")
def logoff():
    if "Username" in session:
        session.pop("Username", None)
        print("logged out")
    return redirect(url_for("home"))

@app.route("/user")
def user():
  if "Username" in session:
    name = session["Username"]
    return f"<h1>{name}</h1>"
  else:
    return redirect(url_for("login"))

@app.route("/profile")
def profile():
  if "Username" in session:
    username = session["Username"]
    password = session["Password"]

    userdata = HoneyBitesDB.get_user_data(username, password)

    username = userdata['username']
    gender = userdata['gender']
    name = userdata['name']
    cuisine_preference = userdata['cuisine_preference']
    cuisines = ', '.join(cuisine_preference)

    if gender == "male":
        pfp = "./static/assets/male.png"
    elif gender == "female":
        pfp = "./static/assets/female.png"

    profile_info = f'''
    <br><br><br>
    <p class="w3-text">{username}</p>
    <br>
    <img style="width: 30%; height:30%;" src={pfp} alt='Profile Picture'>
    <br>
    Name: {name}
    <br>
    My favourite foods are: {cuisines}
    '''
    
    template = render_template("profile.html", profile_info = profile_info)
    response = make_response(template)
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
    return response
  else:
      return redirect(url_for("home"))

@app.route("/get_match") 
def get_match():
    if not "Username" in session:
        return redirect(url_for("home"))
    '''
    Find # others who like the same cuisines the user does
    '''
    #Get Cuisine Preferences from User in Current Session State
    username = session["Username"]
    password = session["Password"]

    # username = "YoBird123"
    # password = "abc123"
    userdata = HoneyBitesDB.get_user_data(username, password)
    cuisines = userdata['cuisine_preference']

    matches = []
    already_matched = []
    p_matches_list = []
    for cuisine in cuisines:   
        p_matches = HoneyBitesDB.get_users_by_preference(cuisine)
        p_matches_list = p_matches_list + p_matches
    for i in range(len(p_matches_list)):
        match = p_matches_list[i]
        print(match)
        if match["username"] != username and match["username"] not in already_matched:
            already_matched.append(match["username"])
            user = match["username"]
            name = match["name"]
            gender = match["gender"]
            cuisines = "+".join(match["cuisine_preference"])
            pfp = ""
            if gender == "male":
                pfp = "./static/assets/male.png"
            elif gender == "female":
                pfp = "./static/assets/female.png"
            info = f'''
            <div class="row" id={i}>
                <div class="column">
                    <p class="button1 w3-button w3-block w3-section w3-black"><button class='button1 w3-button w3-block w3-section' onclick="dash()">Dash</button></p>
                </div>
                <div class="column">
                    <div display: flex; justify-content: center; align-items: center;> 
                        <div style="display: flex; justify-content: center; align-items: center;"><h2>{user}</h2></div> <br>
                        <img style="width: 100%; height:100%;" src={pfp} alt="Profile Picture"> <br>
                        <p class="w3" style="background-color: #FFFF00; text-color: white">Meet {name}!</p> <br>
                        <p class="w3" style="background-color: #FFFF00; text-color: white"> They love {cuisines} food too! </p> <br>
                    </div>
                </div>
                    <div class="column">
                    <form class="w3-container" action="/date" method="POST">
                        <input name="user_data" value={str(match["username"])} hidden>
                        <p class="button1 w3-button w3-block w3-section w3-black"><input type="submit" value="Dine" class="w3-button w3-block w3-section"/></p>
                    </form>
                    </div>
            </div>
            <br>'''
            matches.append(info)


    #Go one by one through and allow User to match

    template = render_template("match.html", matches = matches)
    response = make_response(template)
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
    return response

@app.route("/match")
def match():
    template = render_template("match.html")
    response = make_response(template)
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
    return response

@app.route("/date", methods=["POST", "GET"])
def date():
    data = ""
    if request.method == "POST":
        username = request.form["user_data"]
        print(username)
        data = HoneyBitesDB.get_user_data_unprotected(username)
        m_user = data['username']
        name = data['name']
        gender = data['gender']
        cuisines = data['cuisine_preference']
        cuisines = " + ".join(cuisines)

        if gender == "male":
            pfp = "./static/assets/male.png"
        elif gender == "female":
            pfp = "./static/assets/female.png"
        
        info = f'''<div>
        <br><br><br>
        <p class="w3-text">{m_user}</p>
        <br>
        <img style="width: 30%; height:30%;" src={pfp} alt='Profile Picture'>
        <br>
        <p> Name: {name} </p>
        <br>
        Their favourite foods are: {cuisines}
        '''
        template = render_template("dine.html", info = info)
        response = make_response(template)
        response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
        return response
    return redirect(url_for("home"))
    

if __name__ == "__main__":
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'serviceAccountKey.json'
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    client = oa.initialize()

   

    



