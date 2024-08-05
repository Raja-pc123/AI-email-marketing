from scrapegraphai.graphs import SearchGraph
import requests
import google.generativeai as genai
import os
# import pandas as pd
import re
import streamlit as st
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()
import firebase_admin
import sys
from firebase_admin import firestore
from firebase_admin import credentials
# import nest_asyncio
# nest_asyncio.apply()
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

cred = credentials.Certificate("ai-email-marketing-config.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
    
db=firestore.client()

    
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')



def extract_domain_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    domain_parts = domain.split('.')
    if len(domain_parts) == 2:
        name = domain_parts[0]
        extension = domain_parts[1]
    elif len(domain_parts) > 2:
        name = domain_parts[-2]
        extension = domain_parts[-1]
    else:
        name = ''
        extension = ''
    link= name+'.'+extension
    return name, link


def companyWebScrapper(company):
    prompt_1 = f"About {company} in detail"
    graph_config = {
        "llm": {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "model": "gemini-pro",
        },
    }

    # Create the search graph
    search_graph_1= SearchGraph(prompt_1, graph_config)

    # Run the search graph
    result = search_graph_1.run()

    summ_res= model.generate_content(f""" Summarize the below information in a readble format:
                                      {result}
                                      Include good enough content at the beginning of the text containing almost all information of the company.
                                      Don't include services and solutions of the company.
                                      Also don't include any testimonials or reviews.
                                      Don't include Contact info or Contact emails.
                                      Also Don't include any social media platform and its links.
                                      There should not be any kind of link present in the text.
                                      """)
    
    prompt_2= f"list out all the company services and solutions provided by {company}. "
    search_graph_2 = SearchGraph(prompt_2, graph_config)
    # Run the search graph
    services = search_graph_2.run()
    
    prompt_3 = f"{company} client testimonials" 

    # Create the search graph
    search_graph_3 = SearchGraph(prompt_3, graph_config)
    client_review = search_graph_3.run()
    
    return summ_res.text, services, client_review

def follow_up_email(prof_id,companyDomain):
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    company = db.collection('companyInfo').document(companyDomain).get().to_dict()
    if company['Info']!='':
        print("company info found generating mail.....")
        follow_up_details=db.collection('profile_ID').document(prof_id).get().to_dict()
        message=[]
        if follow_up_details['mails_sent']<= 3:
            if follow_up_details['mails_sent']== 1:
                
                message=[{
                    'role':'user',
                    'parts': f"""Create a follow up email for the software company Pravaah Consulting Inc details mentioned below:
                            {company}
                            Based on the previous mail {follow_up_details['email_1']} and use the follow up word
                            
                            -Include a Subject line 
                            -Dont include client testimonial
                            -Should be about 250 words length not more than that and use 3-4 bullet points saying how we can help you
                            -Output should be in proper HTML format.
                            """}]
                db.collection('profile_ID').document(prof_id).update({'mails_sent':firestore.Increment(1)})

            elif(follow_up_details['mails_sent']== 2):
                message=[{
                    'role':'user',
                    'parts': f"""Create a 2nd follow up email for the software company Pravaah Consulting Inc details mentioned below:
                            {company}
                            Based on the previous follow up mail {follow_up_details['email_2'] } , start the mail saying something like you must have been busy  
                            -Include a different subject line but dont use the word 'Subject'
                            -Mention how our team is going to help you
                            -include the call to action link mentioned above
                            -Dont make the message too long
                            -Dont use bullet points
                            -Dont use the word 'follow up' use something different
                            -Dont use I'm impressed by your work or something else.
                            -Dont repeat the words or sentences used in the previous mail make it different.
                            -Output should be in proper HTML format.
                            """}]
                db.collection('profile_ID').document(prof_id).update({'mails_sent':firestore.Increment(1)})

            elif(follow_up_details['mails_sent']== 3):
                message=[{
                    'role':'user',
                    'parts': f"""Create a final follow up email for the software company Pravaah Consulting Inc details mentioned below:
                            {company}
                            Based on the previous 2nd follow up mail {follow_up_details['email_3']} also mention about 100+ successful projects and satisfied clients who are willing to vouch for our expertise and say something like understanding your valuable time I would love to schedule  a call and request the person to book an appointment.
                            -Use Hello instead of Hi
                            -Include a different subject line but dont use the word 'Subject'
                            -Dont make the message too long
                            -include the call to action link mentioned above
                            -Dont say this is the final time / final follow up / last time , use something like reminder
                            -Dont use I'm impressed by your work or something else.
                            -Dont repeat the words or sentences used in the previous mail make it different.
                            -Output should be in proper HTML format.
                            """}]
                db.collection('profile_ID').document(prof_id).update({'mails_sent':firestore.Increment(1)})

            response=model.generate_content(message, 
            generation_config=genai.types.GenerationConfig(
            temperature=0.7))

            # subject_prompt=[{
            #     'role':'user',
            #     'parts':f""" {response.text}
            #      create only a subject line for this email and dont include the word 'subject'."""
            # }]
            # subject=model.generate_content(subject_prompt,
            # generation_config=genai.types.GenerationConfig(
            # temperature=0.7))

            # cleaned_subject= re.sub(r'[#*]', '', subject.text)

            num=follow_up_details['mails_sent']
            db.collection('profile_ID').document(prof_id).update({f'email_{num+1}':response.text})
            return response.text
           
    
    else:
        print("Company info not found !! **First Send the initial mail**")

def email_generator(name_id,category,companyDomain,companyName,contactLink):
    
   
    url = f"http://localhost:8600/profile/{name_id}" 
    
    
    profile_details = requests.get(url)
    profile=profile_details.json()
    
    if 'undefined' in profile['url']:
        fullName=name_id
        
    else:
        fullName=profile['firstName']+' '+profile['lastName']
    
    if category.lower()=='none':
        category='None'

    company, others, testimonial = companyWebScrapper(companyName)
     
    messages = [{'role':'user',
                    'parts':
    f"""
    Craft an compelling email marketing message for a company named {companyName} from sales representative Raja. The company details are below:
    {company}
     
    {others}
    
    testimonial
    {testimonial}
    
    based on the above details the email should be based on the profile details of {fullName} mentioned below:
    {profile}
    
    The email should contain:
    
    Have a compelling subject line but dont include the word 'Subject'
    Include a personalized greeting and mention some specific points that you liked or learned from the persons profile.
    How the company's services will help him/her for the category {category}  using proper bullet points
    Highlight the benefits and reasons to choose the company.
    Include a call to action for a free consultation at {contactLink}
    If there is a proper client testimonial above then include, otherwise dont include it and it should be in itallic only nothing else
    
    Conclude with a thank you message
    
    also use bold sentences using HTML elements everywhere to make the message look more interesting
    -Remove the bullet point from the client testimonial.
    -Put the client testimonial in a box and apply 'Itallic Style' text.
    """}]
        
    response_1=model.generate_content(messages,
    generation_config=genai.types.GenerationConfig(
    temperature=0.8))
    
    messages.append({'role':'model',
                 'parts':[response_1.text]})

    messages.append({'role':'user',
                 'parts':["""Okay, now perform only the following operation on the message:
                             -Output should be in proper HTML format
                             -For Bold and itallic style using HTML only.
                             -Dont add anything
                             -Make sure not to add anything else other than the mail.
                          """]})

    response_2=model.generate_content(messages,
    generation_config=genai.types.GenerationConfig(
    temperature=0.8))
    
    #storing the email details
    db.collection('profile_ID').document(name_id).set({'email_1':response_2.text,'mails_sent':1})
    db.collection('companyInfo').document(companyDomain).set({'Info':company,'services':others,'client_review':testimonial})
    
    return response_2.text
    
# def extract_data_from_csv(csv_file):
  
#     df = pd.read_csv(csv_file)
#     names = df['name']
#     email_ids = df['email_id']
#     categories = df['category']
#     return names, email_ids, categories
 
def extract_linkedin_name(url):
    pattern = r"linkedin\.com/in/([^/?&]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None
    
def main():
   
    st.title("Email Marketing Message Generator")
     
    # **Note: mass email functionality to be handled later**    
    # if 'csv' not in st.session_state:
    #     st.session_state.csv = None
        
    # csv_file= st.file_uploader("Select the  csv file")
        
    link = st.text_input("Enter Linkedin profile-link:")
    if link:
        name = extract_linkedin_name(link)
        if name:
            pass
        else:
            st.warning("Enter correct LinkedIn Link.")
            
    # email_id=st.text_input("Enter email id: ")
    companyUrl=st.text_input("Enter company URL: ")
    contactLink=st.text_input("Enter company contact link: ")
    category=st.text_input("Enter mail cateory: ")
    
    company_name , company_domain =extract_domain_name(companyUrl)
    
    gen = st.button("Generate Email")
    auto=st.button('Follow-up emails')

    # if csv_file is not None:
    #     st.session_state.csv=csv_file
        
    if 'followUp_email' not in st.session_state:
        st.session_state.followUp_email = False
    
        
    if "gen_state" not in st.session_state:
        st.session_state.gen_state = False

    
    # inital emails
    if gen or st.session_state.gen_state:
        st.session_state.gen_state = True
        with st.spinner("Generating email content..."):
            st.session_state.email_content = []
            
            # ***Note: mass email logic***
            # if csv_file is not None:
            #     name,email_id,category = extract_data_from_csv(csv_file)
            #     st.session_state.email = email_id
            #     for i in range(len(email_id)):
            #         full_email = email_generator(name.iloc[i], category.iloc[i],email_id.iloc[i])
            #         st.session_state.email_content.append(full_email)
                    
            # single email
            #else:
            full_email = email_generator(name, category,company_domain,company_name,contactLink)
            st.session_state.email_content.append(full_email)
            
            st.subheader("Generated Email Content:")
            for i, email in enumerate(st.session_state.email_content, 1):
                st.markdown(email, unsafe_allow_html=True)
                st.markdown("---")
                    
           
  
    # follow-up emails 
    if auto or st.session_state.followUp_email:
        st.session_state.followUp_email = True
        #Note: mass follow-up emails
        # if st.session_state.csv is not None:
            
        #     email_id=st.session_state.email
        #     for i in range(len(email_id)):
        #         for j in range(0,3):
        #             f_email, _ = follow_up_email(email_id.iloc[i])
        #             st.markdown(f_email,unsafe_allow_html=True)
        #             st.markdown("---")
        #     st.success("**follow-up emails generated**")
        
        #single follow-up emails
        #else:
        for i in range(0,3):
            f_email = follow_up_email(name,company_domain)
            st.markdown(f_email,unsafe_allow_html=True)
            st.markdown("---")
        st.success("**follow-up emails generated**")
            
        
       

if __name__ == "__main__":
    main()

