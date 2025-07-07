from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

# configurarea conexiunii la MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.PersonalJournal
entries_collection = db.JournalThoughts

@app.route('/')
def home():
    return redirect(url_for('add_entry'))

@app.route('/index', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':

        title = request.form.get('title')
        thought = request.form.get('thought')
        if thought:
            entry = {
                "thought": thought,
                "title": title,
                "date": datetime.datetime.now()
            }
            entries_collection.insert_one(entry)
            return redirect(url_for('list_entries'))
    return render_template('index.html')

@app.route('/listOfThoughts', methods=['GET', 'POST'])
def list_entries():
    date_filter = request.args.get('date')
    title_filter = request.args.get('title', '').lower()

    query = {} #pt a obitne datele din mongo
    if date_filter:
        try:
            date_filter = datetime.datetime.strptime(date_filter, '%Y-%m-%d') #in obiect
            next_day = date_filter + datetime.timedelta(days=1) #next-day se calculeaza intre ziua de inceput si cea de final;
            query['date'] = {"$gte": date_filter, "$lt": next_day}
        except ValueError:
            pass

    if title_filter:
        query['title'] = {"$regex": title_filter, "$options": "i"}

    entries = list(entries_collection.find(query).sort("date", -1))

    return render_template('listOfThoughts.html', entries=entries)



@app.route('/thoughtDetails/<id>')
def thought_details(id):
    entry = entries_collection.find_one({"_id": ObjectId(id)})
    if not entry:
        return "Gandul nu a fost gasit", 404
    return render_template('thoughtDetails.html', entry=entry)

@app.route('/update/<id>', methods=['POST'])
def update_entry(id):
    new_title = request.form.get('title')
    new_thought = request.form.get('thought')
    entries_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"title": new_title, "thought": new_thought}}
    )
    return redirect(f'/thoughtDetails/{id}')

@app.route('/delete/<id>')
def delete_entry(id):
    entries_collection.delete_one({"_id": ObjectId(id)})
    return redirect('/listOfThoughts')

if __name__ == '__main__':
    app.run(debug=True)
