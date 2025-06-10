import streamlit as st
import requests
import datetime
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import matplotlib.pyplot as plt
import os

# تأكد أن هذا يطابق عنوان URL للـ backend API الخاص بك
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Incident Reporting System", layout="wide")
st.title("🛡️ Incident Reporting System")

menu = st.sidebar.radio("Choose an action", ["Submit Report", "View Reports", "Analytics"])

MAX_FILE_SIZE_MB = 10

def validate_file(file):
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File {file.name} exceeds {MAX_FILE_SIZE_MB}MB limit."
    allowed_exts = ["jpg", "jpeg", "png", "mp4", "avi", "pdf"]
    ext = file.name.split('.')[-1].lower()
    if ext not in allowed_exts:
        return False, f"File {file.name} has an unsupported file type. Allowed types: {', '.join(allowed_exts)}"
    return True, ""

geolocator = Nominatim(user_agent="incident_report_app")

def get_coords_from_location(country, city):
    try:
        # بناء الاستعلام بشكل مرن: إذا لم تكن المدينة موجودة، فابحث عن البلد فقط.
        query_parts = []
        if city and city.strip():
            query_parts.append(city.strip())
        if country and country.strip():
            query_parts.append(country.strip())
            
        query = ", ".join(query_parts)
        
        if not query:
            return None, None # لا يوجد بلد أو مدينة، فلا يمكن تحديد إحداثيات

        # جرب أولاً بالبلد والمدينة معًا، ثم بالبلد فقط إذا فشلت المدينة
        location = None
        if query_parts:
            location = geolocator.geocode(query, timeout=20)
            if not location and len(query_parts) > 1 and country and country.strip(): # إذا فشل البحث بالمدينة والبلد معًا، جرب بالبلد فقط
                 st.info(f"Could not find exact coordinates for '{query}'. Trying to geocode '{country.strip()}' only.")
                 location = geolocator.geocode(country.strip(), timeout=20)

        if location:
            return location.latitude, location.longitude
    except GeocoderTimedOut:
        st.warning("Geocoder timed out. Could not determine coordinates from location name.")
    except Exception as e:
        st.warning(f"An error occurred while geocoding: {e}")
    return None, None


# --- Submit New Incident Report ---
if menu == "Submit Report":
    st.header("📋 Submit a New Incident Report")

    # تهيئة session_state بشكل صحيح ومرة واحدة فقط
    # تم إعادة إحداثيات فلسطين الافتراضية
    if "lat" not in st.session_state:
        st.session_state.lat = 31.9037 # إحداثيات رام الله
    if "lon" not in st.session_state:
        st.session_state.lon = 35.2163 # إحداثيات رام الله
    
    if "country_display_value" not in st.session_state:
        st.session_state.country_display_value = "Palestine"
    if "city_display_value" not in st.session_state:
        st.session_state.city_display_value = "Ramallah" # يمكن جعلها فارغة إذا لم تكن رام الله هي المدينة الافتراضية
                                                         # ولكنك ذكرت Ramallah في وصف السؤال الأصلي

    if "map_clicked_recently" not in st.session_state:
        st.session_state.map_clicked_recently = False

    with st.form("report_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            reporter_type = st.selectbox("Reporter Type", ["Individual", "Organization"])
            anonymous = st.checkbox("Submit Anonymously", value=False)
            date = st.date_input("Incident Date", value=datetime.date.today())
        with col2:
            country_input = st.text_input("Country", value=st.session_state.country_display_value, key="country_input_field")
            city_input = st.text_input("City (optional)", value=st.session_state.city_display_value, key="city_input_field")

        # المنطق المحسّن لتحديث الإحداثيات من حقول النص
        # يتم التحديث فقط إذا تغيرت قيم الحقول ولم يتم النقر على الخريطة مؤخرًا
        if not st.session_state.map_clicked_recently:
            # Check if current input values are different from last stored display values
            # OR if we just started and default values are not yet reflected on the map
            # This logic avoids redundant geocoding and ensures text inputs override map clicks until new click
            if (country_input != st.session_state.country_display_value or \
                city_input != st.session_state.city_display_value) :
                
                lat, lon = get_coords_from_location(country_input, city_input)
                if lat is not None and lon is not None:
                    st.session_state.lat = lat
                    st.session_state.lon = lon
                # else: # If geocoding fails, maybe revert to default or handle as needed
                #     st.session_state.lat = 31.9037 # Fallback to Ramallah
                #     st.session_state.lon = 35.2163 # Fallback to Ramallah

                st.session_state.country_display_value = country_input
                st.session_state.city_display_value = city_input
                st.session_state.map_clicked_recently = False # Ensure map is not marked as clicked if text changed

        st.markdown("### 📍 Select Location on Map or Input Coordinates")

        map_center = [st.session_state.lat, st.session_state.lon]

        # ضبط مستوى التكبير: افتراضيًا 10 (لفلسطين) أو 2 إذا كانت إحداثيات عامة (لم تعد تستخدم)
        # الآن بما أن فلسطين هي الافتراضية، يمكن أن يكون التكبير 10 أو 11
        zoom_level = 10 
        m = folium.Map(location=map_center, zoom_start=zoom_level)

        # Marker يظهر دائماً على الموقع المحدد (سواء كان افتراضياً أو من إدخال المستخدم/النقر)
        if st.session_state.lat is not None and st.session_state.lon is not None:
            folium.Marker([st.session_state.lat, st.session_state.lon], tooltip="Selected Location").add_to(m)

        map_data = st_folium(m, width=700, height=450)

        if map_data and map_data.get("last_clicked"):
            st.session_state.lat = map_data["last_clicked"]["lat"]
            st.session_state.lon = map_data["last_clicked"]["lng"]
            st.toast("Location updated from map click!")
            st.session_state.map_clicked_recently = True
            # عند النقر على الخريطة، يمكن تحديث حقول النص تلقائيًا بالعكس (Reverse Geocoding)
            try:
                # هذا الجزء يحتاج إلى مكتبة geopy لإعادة تحديد اسم المكان من الإحداثيات
                location_from_coords = geolocator.reverse((st.session_state.lat, st.session_state.lon), timeout=20)
                if location_from_coords and location_from_coords.address:
                    address_parts = location_from_coords.raw.get('address', {})
                    # حاول استخراج البلد والمدينة
                    detected_country = address_parts.get('country')
                    detected_city = address_parts.get('city') or address_parts.get('town') or address_parts.get('village')
                    
                    if detected_country:
                        st.session_state.country_display_value = detected_country
                    if detected_city:
                        st.session_state.city_display_value = detected_city
                    else: # If no city, clear the city field
                        st.session_state.city_display_value = ""
                else: # If reverse geocoding fails, clear city/country
                    st.session_state.country_display_value = ""
                    st.session_state.city_display_value = ""
            except GeocoderTimedOut:
                st.warning("Reverse geocoder timed out. Could not determine location name from coordinates.")
            except Exception as e:
                st.warning(f"An error occurred during reverse geocoding: {e}")
            st.rerun() # Re-run to update text fields after map click

        latitude = st.session_state.lat
        longitude = st.session_state.lon
        st.write(f"Selected Coordinates: Latitude {latitude:.6f}, Longitude {longitude:.6f}")
        
        # رسالة تحذير مخصصة للإحداثيات الافتراضية لرام الله (للحث على الدقة)
        if latitude == 31.9037 and longitude == 35.2163 and \
           st.session_state.country_display_value == "Palestine" and st.session_state.city_display_value == "Ramallah":
            st.warning("The map is centered on Ramallah, Palestine. Please click on the map to select the exact incident location, or provide a more specific City.")


        st.markdown("### 📝 Incident Description")
        description = st.text_area("Describe the incident in detail", height=150)

        violation_types = st.text_input(
            "Violation Types (comma-separated)", help="e.g. abuse, torture, arbitrary detention"
        )

        st.markdown("### 📎 Contact Information")
        email_input = None 
        phone_input = None
        preferred_contact_input = None

        if not anonymous:
            email_input = st.text_input("Email", placeholder="reporter@example.com")
            phone_input = st.text_input("Phone Number", placeholder="+972-5X-XXXXXXX")
            preferred_contact_input = st.radio("Preferred Contact Method", ["email", "phone"], horizontal=True)

        st.markdown("### 📁 Upload Evidence Files")
        uploaded_files = st.file_uploader(
            f"Upload files (optional, max {MAX_FILE_SIZE_MB}MB each)",
            type=["jpg", "jpeg", "png", "mp4", "avi", "pdf"],
            accept_multiple_files=True,
        )

        file_errors = []
        if uploaded_files:
            for f in uploaded_files:
                valid, msg = validate_file(f)
                if not valid:
                    file_errors.append(msg)
        if file_errors:
            for err in file_errors:
                st.error(err) 
            st.stop()

        submitted = st.form_submit_button("Submit Report")
        
        status_message_placeholder = st.empty()


        if submitted:
            status_message_placeholder.empty()

            # التحقق من أن الإحداثيات ليست الافتراضية تمامًا (إلا إذا كانت هي الإحداثيات الحقيقية للموقع)
            # تم تعديل الشرط ليكون أكثر دقة
            if latitude == 31.9037 and longitude == 35.2163 and \
               country_input.strip() == "Palestine" and city_input.strip() in ["", "Ramallah"]:
                status_message_placeholder.error("Please click on the map to select a more precise incident location, or provide a more specific City than just 'Ramallah'.")
                st.stop()

            if not description.strip():
                status_message_placeholder.error("Description cannot be empty.")
                st.stop()

            if not violation_types.strip():
                status_message_placeholder.error("Violation types cannot be empty.")
                st.stop()
            
            if not country_input.strip(): 
                status_message_placeholder.error("Country cannot be empty.")
                st.stop()
            
            if not anonymous:
                if not email_input and not phone_input:
                    status_message_placeholder.error("Email or phone is required if you are not submitting anonymously.")
                    st.stop()

            with st.spinner("Submitting report..."):
                files_to_upload = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files] if uploaded_files else []

                data = {
                    "reporter_type": reporter_type,
                    "anonymous": str(anonymous).lower(),
                    "email": email_input if email_input else None,
                    "phone": phone_input if phone_input else None,
                    "preferred_contact": preferred_contact_input if preferred_contact_input else None,
                    "date": date.isoformat(),
                    "country": country_input,
                    "city": city_input if city_input else None,
                    "longitude": longitude,
                    "latitude": latitude,
                    "description": description,
                    "violation_types": violation_types,
                }

                try:
                    response = requests.post(f"{API_URL}/reports/", data=data, files=files_to_upload)
                    if response.status_code == 201:
                        status_message_placeholder.success("✅ Report submitted successfully!")

                        # إعادة تعيين قيم session_state إلى الافتراضيات الأصلية لرام الله
                        st.session_state.lat = 31.9037
                        st.session_state.lon = 35.2163
                        st.session_state.country_display_value = "Palestine"
                        st.session_state.city_display_value = "Ramallah" # إعادة Ramallah كقيمة افتراضية
                        st.session_state.map_clicked_recently = False
                        
                    else:
                        status_message_placeholder.error(f"❌ Error submitting report: {response.status_code} - {response.text}")
                except requests.exceptions.ConnectionError:
                    status_message_placeholder.error("🚫 Failed to connect to the backend API. Please ensure the backend is running.")
                except Exception as e:
                    status_message_placeholder.error(f"🚫 An unexpected error occurred: {e}")


# --- View All Incident Reports ---
elif menu == "View Reports":
    st.header("📂 All Incident Reports")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filter Reports")
    
    filter_status = st.sidebar.selectbox(
        "Filter by Status",
        ["All", "new", "in_progress", "closed", "resolved", "on_hold"],
        key="filter_status"
    )
    
    filter_start_date_enabled = st.sidebar.checkbox("Enable Start Date Filter", value=False)
    filter_start_date = None
    if filter_start_date_enabled:
        filter_start_date = st.sidebar.date_input(
            "Start Date",
            value=datetime.date(2023, 1, 1),
            key="filter_start_date"
        )
    
    filter_end_date_enabled = st.sidebar.checkbox("Enable End Date Filter", value=False)
    filter_end_date = None
    if filter_end_date_enabled:
        filter_end_date = st.sidebar.date_input(
            "End Date",
            value=datetime.date.today(),
            key="filter_end_date"
        )

    filter_country = st.sidebar.text_input("Filter by Country", key="filter_country")
    
    params = {"limit": 100}

    if filter_status and filter_status != "All":
        params["status"] = filter_status
        
    if filter_start_date_enabled and filter_start_date:
        params["start_date"] = filter_start_date.isoformat()
        
    if filter_end_date_enabled and filter_end_date:
        params["end_date"] = filter_end_date.isoformat()
            
    if filter_country:
        params["country"] = filter_country

    try:
        with st.spinner("Fetching reports..."):
            response = requests.get(f"{API_URL}/reports/", params=params)
        
        if response.ok:
            reports = response.json()
            if not reports:
                st.info("No reports found matching the criteria.")
            for report in reports:
                report_id = report.get('report_id', 'N/A')
                incident_details = report.get('incident_details', {})
                location = incident_details.get('location', {})
                country_name = location.get('country', 'Unknown')
                date_str = incident_details.get('date', 'N/A')
                description = incident_details.get('description', 'No description provided.')
                violation_types = incident_details.get('violation_types', [])
                status = report.get('status', 'N/A')
                evidence = report.get('evidence', [])

                with st.expander(f"**Report ID:** {report_id} | **Country:** {country_name} | **Date:** {date_str}"):
                    st.write(f"**Description:** {description}")
                    st.write(f"**Violation Types:** {', '.join(violation_types)}")
                    
                    allowed_statuses = ["new", "in_progress", "closed", "resolved", "on_hold"]
                    current_status_index = allowed_statuses.index(status) if status in allowed_statuses else 0
                    
                    new_status = st.selectbox(
                        f"Update Status for {report_id}",
                        allowed_statuses,
                        index=current_status_index,
                        key=f"status_select_{report_id}"
                    )

                    if new_status != status:
                        if st.button(f"Apply Status Change for {report_id}", key=f"apply_status_btn_{report_id}"):
                            try:
                                update_response = requests.patch(
                                    f"{API_URL}/reports/{report_id}",
                                    json={"status": new_status}
                                )
                                if update_response.status_code == 200:
                                    st.success(f"Status for Report {report_id} updated to {new_status}!")
                                    st.rerun() 
                                else:
                                    st.error(f"Failed to update status for Report {report_id}: {update_response.status_code} - {update_response.text}")
                            except requests.exceptions.ConnectionError:
                                st.error("🚫 Failed to connect to the backend API for status update. Is the backend running?")
                            except Exception as e:
                                st.error(f"🚫 An unexpected error occurred during status update: {e}")
                    else:
                        st.write(f"**Current Status:** {status}")

                    if report.get('anonymous') == False and report.get('contact_info'):
                        st.markdown("**Contact Information:**")
                        contact = report['contact_info']
                        if contact.get('email'): st.write(f"Email: {contact['email']}")
                        if contact.get('phone'): st.write(f"Phone: {contact['phone']}")
                        if contact.get('preferred_contact'): st.write(f"Preferred Contact: {contact['preferred_contact']}")
                    else:
                        st.write("**Contact:** Anonymous")

                    if evidence:
                        st.markdown("**Evidence Files:**")
                        for ev in evidence:
                            ev_type = ev.get('type', 'document')
                            ev_url = ev.get('url')
                            ev_desc = ev.get('description', '')
                            
                            if ev_url:
                                full_url = f"{API_URL}{ev_url}"
                                if ev_type == "photo":
                                    st.image(full_url, caption=ev_desc, width=250)
                                elif ev_type == "video":
                                    st.video(full_url)
                                else:
                                    st.markdown(f"[{ev_type.capitalize()}]: [{os.path.basename(ev_url)}]({full_url})")
                            else:
                                st.write(f"[{ev_type.capitalize()}] No URL available.")
        else:
            st.error(f"Failed to fetch reports. Status code: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("🚫 Failed to connect to the backend API. Please ensure the backend is running.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


# --- Violation Type Analytics ---
elif menu == "Analytics":
    st.header("📊 Violation Type Analytics")
    try:
        with st.spinner("Fetching analytics data..."):
            response = requests.get(f"{API_URL}/reports/analytics")
        
        if response.ok:
            data = response.json()
            if not data:
                st.info("No analytics data available. Submit some reports first!")
            else:
                labels = [item["violation_type"] for item in data]
                counts = [item["count"] for item in data]

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(labels, counts, color="skyblue") 
                plt.xticks(rotation=45, ha="right")
                plt.ylabel("Number of Incidents")
                plt.xlabel("Violation Type")
                plt.title("Incident Reports by Violation Type")
                plt.tight_layout()
                st.pyplot(fig) 
        else:
            try:
                error_detail = response.json().get("detail", response.text)
                st.error(f"Could not fetch analytics data. Status code: {response.status_code} - {error_detail}")
            except:
                st.error(f"Could not fetch analytics data. Status code: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("🚫 Failed to connect to the backend API. Please ensure the backend is running.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
