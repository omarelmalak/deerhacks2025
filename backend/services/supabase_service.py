from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_experience(data):
    return supabase.table("experience").insert([data]).execute()

def create_roadmap(user_id):
    return supabase.table('roadmap').insert({'user_id': user_id}).execute()

def insert_user(data):
    return supabase.table("user").insert([data]).execute()

def get_user_by_email(email):
    return supabase.table("user").select("*").eq("email", email).execute()

def get_cleaned_experience(user_id):
        return supabase.table("experience").select("*").eq("user_id", user_id).eq("in_resume", True).execute()
