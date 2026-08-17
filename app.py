import os
import re
import time
import csv
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Directory where CSVs will be saved (uses /tmp on Vercel serverless)
if os.environ.get('VERCEL') or not os.access(os.path.dirname(os.path.abspath(__file__)), os.W_OK):
    DATA_DIR = '/tmp'
else:
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_URL = "https://maps.googleapis.com/maps/api/place/"

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '_', text)
    return text.strip('_')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/history')
def get_history():
    files = []
    try:
        for f in os.listdir(DATA_DIR):
            if f.endswith('.csv') and f.startswith('google_places_'):
                path = os.path.join(DATA_DIR, f)
                files.append({
                    "filename": f,
                    "size": os.path.getsize(path),
                    "modified": os.path.getmtime(path)
                })
        # sort by modified desc
        files.sort(key=lambda x: x['modified'], reverse=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(files)

@app.route('/api/download/<filename>')
def download_file(filename):
    if not filename.endswith('.csv') or '..' in filename:
        return jsonify({"error": "Invalid file format"}), 400
    return send_from_directory(DATA_DIR, filename, as_attachment=True)

DEFAULT_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "AIzaSyCnc0z8deZ5ypklObkR_8DWJRn_zK8iD-k")

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    kueri = data.get('kueri')
    daerah = data.get('daerah')
    radius = data.get('radius')
    api_key = data.get('api_key') or DEFAULT_API_KEY

    if not kueri or not api_key:
        return jsonify({"error": "Kueri and API Key are required"}), 400

    # Combine kueri and daerah for Text Search
    if daerah:
        query = f"{kueri} {daerah}"
    else:
        query = kueri

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.location,places.reviews,places.photos,nextPageToken"
    }
    payload = {
        "textQuery": query,
        "languageCode": "id"
    }

    try:
        print(f"[DEBUG] Calling Places (New) page 1 for query: {query}")
        response = requests.post(url, headers=headers, json=payload)
        print(f"[DEBUG] Places (New) page 1 response code: {response.status_code}")
        res_data = response.json()

        if response.status_code == 200:
            places = []
            for place in res_data.get("places", []):
                loc = place.get("location", {})
                raw_reviews = place.get("reviews", [])
                parsed_reviews = []
                for r in raw_reviews:
                    parsed_reviews.append({
                        "Author": r.get("authorAttribution", {}).get("displayName", "N/A"),
                        "Rating Ulasan": r.get("rating", "N/A"),
                        "Teks Ulasan": r.get("text", {}).get("text", "N/A"),
                        "Waktu Ulasan": r.get("relativePublishTimeDescription", "N/A")
                    })
                
                raw_photos = place.get("photos", [])
                photo_urls = []
                for ph in raw_photos[:5]:
                    ph_name = ph.get("name")
                    if ph_name:
                        photo_urls.append(f"https://places.googleapis.com/v1/{ph_name}/media?maxHeightPx=400&maxWidthPx=400&key={api_key}")

                places.append({
                    "place_id": place.get("id"),
                    "Nama Juice Buah": place.get("displayName", {}).get("text", "N/A"),
                    "Rating": place.get("rating", "N/A"),
                    "Total Reviews": place.get("userRatingCount", "N/A"),
                    "Alamat": place.get("formattedAddress", "N/A"),
                    "lat": loc.get("latitude"),
                    "lng": loc.get("longitude"),
                    "Ulasan": parsed_reviews,
                    "Foto": photo_urls,
                    "FotoSampul": photo_urls[0] if photo_urls else None
                })
            
            print(f"[DEBUG] Page 1 loaded {len(places)} places. Next page token exists: {res_data.get('nextPageToken') is not None}")
            return jsonify({
                "success": True,
                "places": places,
                "next_page_token": res_data.get("nextPageToken"),
                "status": "OK"
            })
        else:
            err_msg = res_data.get('error', {}).get('message', 'No error details provided.')
            print(f"[DEBUG] Page 1 error: {err_msg}")
            return jsonify({"error": f"API Error: {response.status_code} - {err_msg}"}), 400

    except Exception as e:
        print(f"[DEBUG] Page 1 exception: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search_next', methods=['POST'])
def search_next():
    data = request.json
    print(f"[DEBUG] Received data in search_next: {data}")
    next_page_token = data.get('next_page_token')
    api_key = data.get('api_key') or DEFAULT_API_KEY
    kueri = data.get('kueri')
    daerah = data.get('daerah')

    if not next_page_token or not api_key:
        return jsonify({"error": "Next page token and API Key are required"}), 400

    if daerah:
        query = f"{kueri} {daerah}"
    else:
        query = kueri

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.location,places.reviews,places.photos,nextPageToken"
    }
    payload = {
        "textQuery": query,
        "pageToken": next_page_token,
        "languageCode": "id"
    }

    try:
        print(f"[DEBUG] Calling Places (New) next page for query: {query}")
        response = requests.post(url, headers=headers, json=payload)
        print(f"[DEBUG] Places (New) next page response code: {response.status_code}")
        res_data = response.json()

        if response.status_code == 200:
            places = []
            for place in res_data.get("places", []):
                loc = place.get("location", {})
                raw_reviews = place.get("reviews", [])
                parsed_reviews = []
                for r in raw_reviews:
                    parsed_reviews.append({
                        "Author": r.get("authorAttribution", {}).get("displayName", "N/A"),
                        "Rating Ulasan": r.get("rating", "N/A"),
                        "Teks Ulasan": r.get("text", {}).get("text", "N/A"),
                        "Waktu Ulasan": r.get("relativePublishTimeDescription", "N/A")
                    })
                
                raw_photos = place.get("photos", [])
                photo_urls = []
                for ph in raw_photos[:5]:
                    ph_name = ph.get("name")
                    if ph_name:
                        photo_urls.append(f"https://places.googleapis.com/v1/{ph_name}/media?maxHeightPx=400&maxWidthPx=400&key={api_key}")

                places.append({
                    "place_id": place.get("id"),
                    "Nama Juice Buah": place.get("displayName", {}).get("text", "N/A"),
                    "Rating": place.get("rating", "N/A"),
                    "Total Reviews": place.get("userRatingCount", "N/A"),
                    "Alamat": place.get("formattedAddress", "N/A"),
                    "lat": loc.get("latitude"),
                    "lng": loc.get("longitude"),
                    "Ulasan": parsed_reviews,
                    "Foto": photo_urls,
                    "FotoSampul": photo_urls[0] if photo_urls else None
                })
            
            print(f"[DEBUG] Next page loaded {len(places)} places. Next page token exists: {res_data.get('nextPageToken') is not None}")
            return jsonify({
                "success": True,
                "places": places,
                "next_page_token": res_data.get("nextPageToken"),
                "status": "OK"
            })
        else:
            err_msg = res_data.get('error', {}).get('message', 'No error details provided.')
            print(f"[DEBUG] Next page error: {err_msg}")
            return jsonify({
                "success": False,
                "error": f"API Error: {response.status_code} - {err_msg}",
                "status": "ERROR"
            })

    except Exception as e:
        print(f"[DEBUG] Next page exception: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/save_csv', methods=['POST'])
def save_csv():
    data = request.json
    places = data.get('places', [])
    query = data.get('query', 'query')

    if not places:
        return jsonify({"error": "No places to save"}), 400

    try:
        file_name = f"google_places_{slugify(query)}.csv"
        file_path = os.path.join(DATA_DIR, file_name)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Nama Juice Buah", "Rating", "Total Reviews", "Alamat", "Latitude", "Longitude", "Place ID", "Foto Sampul"])
            for p in places:
                foto_cover = p.get("FotoSampul") or (p.get("Foto")[0] if p.get("Foto") else "")
                writer.writerow([
                    p.get("Nama Juice Buah") or p.get("name"),
                    p.get("Rating") or p.get("rating"),
                    p.get("Total Reviews") or p.get("user_ratings_total"),
                    p.get("Alamat") or p.get("formatted_address"),
                    p.get("lat"),
                    p.get("lng"),
                    p.get("place_id"),
                    foto_cover
                ])
        return jsonify({
            "success": True,
            "filename": file_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews', methods=['POST'])
def fetch_reviews():
    data = request.json
    places = data.get('places', [])
    api_key = data.get('api_key') or DEFAULT_API_KEY
    query = data.get('query', 'query')
    language = data.get('language', 'id')

    if not api_key:
        return jsonify({"error": "API Key is required"}), 400
    if not places:
        return jsonify({"error": "No places selected"}), 400

    endpoint = "details/json"
    all_detailed_places = []
    
    try:
        for idx, place in enumerate(places):
            place_id = place.get("place_id")
            if not place_id:
                continue
                
            params = {
                "place_id": place_id,
                "key": api_key,
                "language": language,
                "fields": "name,rating,formatted_address,user_ratings_total,reviews"
            }
            
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
            res_data = response.json()
            
            if res_data["status"] == "OK":
                details = res_data["result"]
                combined_data = {
                    "place_id": place_id,
                    "Nama Juice Buah": details.get("name", "N/A"),
                    "Rating": details.get("rating", "N/A"),
                    "Total Reviews": details.get("user_ratings_total", "N/A"),
                    "Alamat": details.get("formatted_address", "N/A"),
                    "lat": place.get("lat"),
                    "lng": place.get("lng"),
                    "Ulasan": []
                }
                
                reviews = details.get("reviews", [])
                for r in reviews:
                    combined_data["Ulasan"].append({
                        "Author": r.get("author_name", "N/A"),
                        "Rating Ulasan": r.get("rating", "N/A"),
                        "Teks Ulasan": r.get("text", "N/A"),
                        "Waktu Ulasan": r.get("relative_time_description", "N/A")
                    })
                all_detailed_places.append(combined_data)
            else:
                # Fallback
                all_detailed_places.append({
                    "place_id": place_id,
                    "Nama Juice Buah": place.get("Nama Juice Buah") or place.get("name"),
                    "Rating": place.get("Rating") or place.get("rating"),
                    "Total Reviews": place.get("Total Reviews") or place.get("user_ratings_total"),
                    "Alamat": place.get("Alamat") or place.get("formatted_address"),
                    "lat": place.get("lat"),
                    "lng": place.get("lng"),
                    "Ulasan": []
                })
            
            # rate limit detail calls slightly to respect API limits
            time.sleep(0.5)

        query_slug = slugify(query)
        
        # Save CSV 1: Reviews summary
        summary_filename = f"google_places_reviews_summary_{query_slug}.csv"
        with open(os.path.join(DATA_DIR, summary_filename), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Nama Juice Buah", "Rating", "Total Reviews", "Alamat", "Ulasan (Ringkasan)"])
            for p in all_detailed_places:
                summary_text = "; ".join([r["Teks Ulasan"] for r in p["Ulasan"]]) if p["Ulasan"] else "Tidak ada ulasan."
                writer.writerow([
                    p["Nama Juice Buah"],
                    p["Rating"],
                    p["Total Reviews"],
                    p["Alamat"],
                    summary_text
                ])

        # Save CSV 2: Individual reviews
        all_individual_reviews = []
        for p in all_detailed_places:
            for r in p["Ulasan"]:
                all_individual_reviews.append({
                    "Nama Juice Buah": p["Nama Juice Buah"],
                    "Rating Tempat": p["Rating"],
                    "Total Reviews Tempat": p["Total Reviews"],
                    "Alamat Tempat": p["Alamat"],
                    "Author Ulasan": r["Author"],
                    "Rating Ulasan": r["Rating Ulasan"],
                    "Teks Ulasan": r["Teks Ulasan"],
                    "Waktu Ulasan": r["Waktu Ulasan"]
                })
        
        individual_filename = f"google_places_individual_reviews_{query_slug}.csv"
        with open(os.path.join(DATA_DIR, individual_filename), 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Nama Juice Buah", "Rating Tempat", "Total Reviews Tempat", "Alamat Tempat", "Author Ulasan", "Rating Ulasan", "Teks Ulasan", "Waktu Ulasan"])
            for r in all_individual_reviews:
                writer.writerow([
                    r["Nama Juice Buah"],
                    r["Rating Tempat"],
                    r["Total Reviews Tempat"],
                    r["Alamat Tempat"],
                    r["Author Ulasan"],
                    r["Rating Ulasan"],
                    r["Teks Ulasan"],
                    r["Waktu Ulasan"]
                ])
        
        return jsonify({
            "success": True,
            "detailed_places": all_detailed_places,
            "summary_filename": summary_filename,
            "individual_filename": individual_filename
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/single_place_reviews', methods=['POST'])
def fetch_single_place_reviews():
    data = request.json
    place_id = data.get('place_id')
    api_key = data.get('api_key') or DEFAULT_API_KEY
    language = data.get('language', 'id')

    if not place_id or not api_key:
        return jsonify({"error": "place_id and api_key are required"}), 400

    endpoint = "details/json"
    params = {
        "place_id": place_id,
        "key": api_key,
        "language": language,
        "fields": "name,rating,formatted_address,user_ratings_total,reviews,photos"
    }

    try:
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        res_data = response.json()

        if res_data.get("status") == "OK":
            details = res_data.get("result", {})
            reviews = []
            for r in details.get("reviews", []):
                reviews.append({
                    "Author": r.get("author_name", "N/A"),
                    "Rating Ulasan": r.get("rating", "N/A"),
                    "Teks Ulasan": r.get("text", "N/A"),
                    "Waktu Ulasan": r.get("relative_time_description", "N/A")
                })

            photos = []
            for ph in details.get("photos", [])[:5]:
                pref = ph.get("photo_reference")
                if pref:
                    photos.append(f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=600&maxheight=400&photo_reference={pref}&key={api_key}")

            return jsonify({
                "success": True,
                "reviews": reviews,
                "photos": photos
            })
        else:
            err_msg = res_data.get("error_message") or res_data.get("status", "Error fetching details")
            return jsonify({"error": err_msg}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

