import requests
import google.generativeai as genai
import os
import re
import firebase_admin
import falcon
from pprint import pprint
import json
from pydantic import BaseModel, Field 
from urllib.parse import urlparse
from firebase_admin import firestore
from firebase_admin import credentials
from scrapegraphai.graphs import SearchGraph
from langchain_core.output_parsers.json import OutputParserException
from dotenv import load_dotenv
load_dotenv()

#Authorizing the firebase DB
cred = credentials.Certificate("ai-email-marketing-config.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

#initializing the DB
db=firestore.client()

##initializing the gemini model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

#defining the class parameters
class InputParams(BaseModel):
   
    link :str = Field(..., description="Enter LinkedIn profile url")
    companyUrl : str = Field(..., description="Enter company URL")
    contactLink :str = Field(..., description="Enter company contact link ")
    category :str = Field(..., description="Enter mail cateory ")
    sender :str = Field(..., description="Sender name")
    

def get_profile(handle):
    try:
        headers = {
            "accept": "application/vnd.linkedin.normalized+json+2.1",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "csrf-token": "ajax:0875620517677693679",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "cookie": "bcookie=\"v=2&f5398b39-f390-4375-824d-f32f3cdca49b\"; bscookie=\"v=1&202205250601082c71b53f-fdc2-44fa-8cfb-6b21bf2f94f6AQHZX9hl0jRWMdrwnrnB3RD4BaPGoyci\"; li_sugr=2dc829a3-82d3-4d55-8029-131c5896d0e1; g_state={\"i_l\":0}; li_theme=light; li_theme_set=app; li_rm=AQFTPgNbASxDfQAAAY0ccEPIcv7OsYIhPbj2l94TvDqJBD2QJJBmZJoXm2NAvUBXHsS_gtZtlF2mbQrBp_EV2dHHCvMgPHKqRPGTpds_Vt91z5EnXFH1iCBjJIFOSsbJGr-vCzxU1_4oRupMZGOEpLllHhbELn04P7BF30cByyRfcuTcCMRw68-ExlSZLGR9wCRW98dedhRSF61AgSaYcBqdVrHCF2o4lcocdTB-qJQw1cKjuIj2VPCIdNzwvlZeLe4-sycofB9mHvU5kSR0WmA9HQSOUi9JbCrS0KQSF5WmxvvcdUd3QlOF2jqkfSWSKv5-FMmo4du31pSLpFY; visit=v=1&M; _uetvid=6cda5cd0b60211eea18f55e90ab28e1c; dfpfpt=22d7b94efce0480ab2ee4094b4c10e96; _guid=441db49e-478f-424c-9aaf-d073c276d210; timezone=Asia/Calcutta; aam_uuid=60139463412087057011204905824326692127; s_fid=76B06EA5D68A52A3-0FA7C28D26FA5F0C; li_at=AQEDATMsYfQCk9k8AAABkE47Kc8AAAGQcketz1YAVKMhAFkPHipBn4CbwhXr3QuC7eioD6gSErJ22aQiA0O0-5l-qj67pm16XIraDNnQ9Ss_a64tmvL6TNm_i8_JnCpB9RgfiXoxvgSK4iF75JbWZqlo; liap=true; JSESSIONID=\"ajax:0875620517677693679\"; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19900%7CMCMID%7C60334110801953898061186558082725469908%7CMCAAMLH-1719921239%7C12%7CMCAAMB-1719921239%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1719323639s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-1298978213; lang=v=2&lang=en-us; at_check=true; gpv_pn=developer.linkedin.com%2F; s_plt=4.55; s_pltp=developer.linkedin.com%2F; s_tp=3024; s_cc=true; mbox=PC#465c5ec305094ed6bbfc8a461d7d48b8.41_0#1735016658|session#cb5939b640d34fa69f3f5e842b917d57#1719466518; s_ips=814.669565320015; s_ppv=developer.linkedin.com%2F%2C100%2C27%2C3023%2C3%2C3; s_tslv=1719464683880; AnalyticsSyncHistory=AQJMQ2B-z9y1PgAAAZBYF4sunDtDxREQ2Y1eeNNy-il43ekpDPeqMBlu9M5VF_Mmsz0l_Ow4Hq-uhtFqjWuP7A; lms_ads=AQEA7qKS2c914wAAAZBYF4xXt--RuZm2CIPki_r33MPIRj18Kq0WoH6xBy0dVSOYMX6Xk6z1VHTuRiGbhUfcnVmxrc7Sd6Yp; lms_analytics=AQEA7qKS2c914wAAAZBYF4xXt--RuZm2CIPki_r33MPIRj18Kq0WoH6xBy0dVSOYMX6Xk6z1VHTuRiGbhUfcnVmxrc7Sd6Yp; fptctx2=taBcrIH61PuCVH7eNCyH0CYjjbqLuI8XF8pleSQW5Na7f6gRpm4iSu4PmKPWsP2DHBLABtF%252fYG32L6jn0Oi4PqjPpyoym7zPyStRvIlej32IzPh8g1ax8gpyCV0JEXdgibGgyMKmpMgYsfdD5%252fuVXe2vPYbE482RqJARpyd9uApMlOw2iQs%252fkYInw0o%252fzu46QroV3PCYRvM5uX1Lj9A5MgynjCVh%252bIA0Ca0c3xBa9%252bktTWNLbwYtexSyqmWCc42XI2gkd60WrcKHTias2ToCMaiam3JgyPK102cXLEUURsmiyCEMAImRioBlHQ7hpLVmfQlB92y%252bGPE%252b54M%252fkAsESOMbdsj4CZL%252fcHo9q%252bM8fXk%253d; lidc=\"b=OB76:s=O:r=O:a=O:p=O:g=3072:u=478:x=1:i=1719470195:t=1719551045:v=2:sig=AQFYQPsyJQO68k-MFVsXCYEqAjq6Mm8q\"; UserMatchHistory=AQIpKallJDHLaQAAAZBYa8aP8OlgM-PS5cHN43g-t9Azg5UtzUpcF-R20oQVqn0HErjMCGyhsZyUZj9EkNjTsOPE5nuNfhcWjHnLln-Il9K4_fnjVXNjZHP8rQn6aHYOcX6dRhHiUl21Ynvz3w3mQcGsFvKNefA3CLGvfIpQtN8t_nsXbKMkNNdh8AKEH0gW_dSvToZd3sWJbpXzMrUArd9GRcm5OHomb1k-zyVUujMKwHHtMwXD-1-lL0vhiJijPpssYuTSb82QKJoRSR4oJ6ppi7__Y6f9GGDwyjAzwb_TIFcOyNTfbC1tdMqsFMKhupApQudlfURl_BSBLsGou-rAZ81gMRccDYbM2h09fWw-Rwgl9g",
            "Referer": f"https://www.linkedin.com/in/{handle}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        response = requests.get(
            f'https://www.linkedin.com/voyager/api/identity/profiles/{handle}/profileView',
            headers=headers
        )
        
        data = response.json()
        
        entity_with_all_data = next((d for d in data['included'] if d.get('publicIdentifier')), None)
        courses = [d for d in data['included'] if d['$type'] == 'com.linkedin.voyager.identity.profile.Course']
        school_names = [d for d in data['included'] if d['$type'] == 'com.linkedin.voyager.entities.shared.MiniSchool']
        education = [d for d in data['included'] if d['$type'] == 'com.linkedin.voyager.identity.profile.Education']
        experience = [d for d in data['included'] if d['$type'] == 'com.linkedin.voyager.identity.profile.Position']
        profile_summary = next((d for d in data['included'] if d['$type'] == 'com.linkedin.voyager.identity.profile.Profile'), None)
        
        return {
            'firstName': entity_with_all_data.get('firstName'),
            'lastName': entity_with_all_data.get('lastName'),
            'currentOccupation': entity_with_all_data.get('occupation'),
            'aboutSection': profile_summary.get('summary'),
            'country': profile_summary.get('geoCountryName'),
            'city': profile_summary.get('geoLocationName'),
            'handle': entity_with_all_data.get('publicIdentifier'),
            'url': f"https://www.linkedin.com/in/{entity_with_all_data.get('publicIdentifier')}/",
            'courseNames': [course['name'] for course in courses],
            'schools': [school['schoolName'] for school in school_names],
            'schoolDetails': [
                f"schoolName: {details.get('schoolName')}, degreeName: {details.get('degreeName')}, fieldOfStudy: {details.get('fieldOfStudy')}, startDate: {details.get('timePeriod', {}).get('startDate', {}).get('year')}, endDate: {details.get('timePeriod', {}).get('endDate', {}).get('year')}" 
                for details in education
            ],
            'experienceDetails': [
                f"company: {details.get('companyName')}, description: {details.get('description')}, location: {details.get('geoLocationName')}, title: {details.get('title')}, startDate: month: {details.get('timePeriod', {}).get('startDate', {}).get('month')} year: {details.get('timePeriod', {}).get('startDate', {}).get('year')}, endDate: month: {details.get('timePeriod', {}).get('endDate', {}).get('month')} year: {details.get('timePeriod', {}).get('endDate', {}).get('year')}" 
                for details in experience
            ]
        }
    except Exception as e:
        print("Error at get_profile:", str(e))
        return None
    
    
# comapany name & domain extractor 
def extract_domain_name(url):
    parsed_url = urlparse(url)
    domain = str(parsed_url.netloc)
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

def companyInfo(company):
    companyName,_= extract_domain_name(company)
    prompt_1 = f"About {companyName} in detail"
    graph_config = {
        "llm": {
            "api_key":  os.getenv("GOOGLE_API_KEY"),
            "model": "gemini-pro",
        },
    }
    # Create the search graph
    search_graph_1 = SearchGraph(prompt_1, graph_config)
    # Run the search graph
    try:
      result = search_graph_1.run()
    except OutputParserException as e:
      result='NA'
    if result=='NA':
      summ_res = model.generate_content(f"""About {company} company in detail

                                          -Don't include any testimonials or reviews.
                                          -Don't include Contact info or Contact emails.
                                          -Don't include any social media platform and its links.
                                          -There should not be any kind of link present in the text.""")
    else:
      summ_res = model.generate_content(f""" Summarize the below information in a readable format:
                                          {result}
                                          Include good enough content at the beginning of the text containing almost all information of the company.
                                          Don't include services and solutions of the company.
                                          Also don't include any testimonials or reviews.
                                          Don't include Contact info or Contact emails.
                                          Also Don't include any social media platform and its links.
                                          There should not be any kind of link present in the text.
                                          """)
    prompt_2 = f"list out all the company services and solutions provided by {company}. "
    search_graph_2 = SearchGraph(prompt_2, graph_config)
    # Run the search graph
    try:
      services = search_graph_2.run()
    except OutputParserException as e:
      services='NA'
    prompt_3 = f"{company} client testimonials"
    # Create the search graph
    search_graph_3 = SearchGraph(prompt_3, graph_config)
    try:
      client_review = search_graph_3.run()
    except OutputParserException as e:
      client_review='NA'

    # Prepare the response
    response = {
        'text': summ_res.text,
        'services': services,
        'review': client_review
    }
    return response
     
# LinkedIN profile handle extractor
def extract_linkedin_name(url):
    pattern = r"linkedin\.com/in/([^/?&]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise falcon.HTTPNotFound(description="LinkedIn Account Not Found. **Try with an actual account.**")

# follow-up email api endpoint
class FollowUpEmailResource:  
    def on_post(self, req, resp):
        #data = await req.get_media()
        data = json.load(req.bounded_stream)
        prof_id = str(data.get('prof_id'))
        company_url = str(data.get('companyUrl'))

        prof_id = req.get_param('prof_id')
        company_url = req.get_param('companyUrl')

        model = genai.GenerativeModel('gemini-1.5-flash')

        _,fullDomainName = extract_domain_name(company_url)
        profileID=extract_linkedin_name(prof_id)

        #checking company and person information in the database
        company_info = db.collection('companyInfo').document(fullDomainName).get().to_dict()
        person_id=db.collection('generatedEmail').document(profileID).get().to_dict()

        if company_info and person_id :
            # checking if person_id has received the initial email from a company 
            if db.collection('generatedEmail').document(profileID).get().to_dict()['email_from_company']==fullDomainName:

                result=[]
                for i in range(0,3):

                    follow_up_details=db.collection('generatedEmail').document(profileID).get().to_dict()
                    message=[]

                    #reseting the db to regenerate the mails again
                    if follow_up_details['mails_sent']== 4:
                        db.collection('generatedEmail').document(profileID).update({'mails_sent':1})

                    #checking number of follow-up emails sent [max 3 allowed]
                    if follow_up_details['mails_sent']== 1:
                    
                        message=[{
                            'role':'user',
                            'parts': f"""Create a follow up email for the software company Pravaah Consulting Inc details mentioned below:
                                    {company_info}
                                    Based on the previous mail {follow_up_details['email_1']} and use the follow up word

                                    -Include a Subject line
                                    -Dont include client testimonial
                                    -Should be about 250 words length not more than that and use 3-4 bullet points saying how we can help you
                                    -Output should be in proper HTML format.
                                    """}]
                        db.collection('generatedEmail').document(profileID).update({'mails_sent':firestore.Increment(1)})

                    elif(follow_up_details['mails_sent']== 2):
                        message=[{
                            'role':'user',
                            'parts': f"""Create a 2nd follow up email for the software company Pravaah Consulting Inc details mentioned below:
                                    {company_info}
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
                        db.collection('generatedEmail').document(profileID).update({'mails_sent':firestore.Increment(1)})

                    elif(follow_up_details['mails_sent']== 3):
                        message=[{
                            'role':'user',
                            'parts': f"""Create a final follow up email for the software company Pravaah Consulting Inc details mentioned below:
                                    {company_info}
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
                        db.collection('generatedEmail').document(profileID).update({'mails_sent':firestore.Increment(1)})

                    #fetching the response from gemini     
                    response=model.generate_content(message, 
                    generation_config=genai.types.GenerationConfig(
                    temperature=0.8))

                    num=follow_up_details['mails_sent']
                    db.collection('generatedEmail').document(profileID).update({f'email_{num+1}':response.text})

                    result.append(response.text) # storing the follow-up emails
                resp.media = {'email_1': result[0], 'email_2': result[1], 'email_3': result[2]}
        
        else:
        # exception handling
            raise  falcon.HTTPNotFound(description=f"Company {fullDomainName} info not found for the LinkedIN ID: {prof_id}!!  **First Send the initial mail**")


# email content generation api endpoint
class EmailGeneratorResource:
    def on_post(self, req, resp):
     
        # data = await req.get_media()
        # item = InputParams(**data)
        
        item = InputParams(**req.media)
        name_id = extract_linkedin_name(item.link)
        
        profile=get_profile(name_id)
        
        #checking the existence of the linkedin profile and storing the info in firebase
        if profile==None:
            fullName=name_id
            raise  falcon.HTTPNotFound(description="LinkedIn profile not found!")

        else:
            fullName=profile['firstName']+' '+profile['lastName']
            db.collection('linkedInData').document(name_id).set({'profileData':str(profile)})        

        if item.category.lower()=='':
            item.category='None'

        
        fetched_company_info = companyInfo(item.companyUrl) 
        
        companyName,fullDomainName= extract_domain_name(item.companyUrl)

       
        #prompt for email generation
        messages = [{'role':'user',
                        'parts':
        f"""
        Craft an compelling email marketing message for a company named {companyName} from Sales Representative {item.sender}. The company details are below:
        {fetched_company_info['text']}

        {fetched_company_info['services']}

        testimonial 
        {fetched_company_info['review']}

        based on the above details the email should be based on the profile details of {fullName} mentioned below:
        {profile}

        The email should contain:

        Have a compelling subject line but dont include the word 'Subject'
        Include a personalized greeting and mention some specific points that you liked or learned from the persons profile.
        How the company's services will help him for the category {item.category}  using proper bullet points
        Highlight the benefits and reasons to choose the company.
        Include a call to action for a free consultation at link: {item.contactLink}
        If there is a proper client testimonial of {companyName} above then include it using word (Testimonial), otherwise dont include it and it should be in itallic only nothing else

        Conclude with a thank you message
        

        also use bold sentences using HTML elements everywhere to make the message look more interesting
        -Remove the bullet point from the client testimonial.
        -Put the client testimonial in a box (dont highlight it) and apply 'Itallic Style' text.

        """}]

        #initial response     
        response_1=model.generate_content(messages,
        generation_config=genai.types.GenerationConfig(
        temperature=0.8))

        messages.append({'role':'model',
                     'parts':[response_1.text]})

        #refining the generated email
        messages.append({'role':'user',
                     'parts':["""Okay, now perform only the following operation on the message:
                                 -Output should be in proper HTML format
                                 -For Bold and itallic style using HTML only.
                                 -Dont add anything
                                 -Make sure not to add anything else other than the mail.
                              """]})
        #final response
        response_2=model.generate_content(messages,
        generation_config=genai.types.GenerationConfig(
        temperature=0.8))

        #storing the email details
        db.collection('generatedEmail').document(name_id).set({'email_1':response_2.text,'mails_sent':1,'email_from_company':fullDomainName})
        db.collection('companyInfo').document(fullDomainName).set({'info':fetched_company_info['text'],'services':fetched_company_info['services'],'client_review':fetched_company_info['review']})

        resp.media = response_2.text

app=falcon.App()
app.add_route('/follow_up_email', FollowUpEmailResource())
app.add_route('/gen_email', EmailGeneratorResource())

if __name__ == "__main__":
    from waitress import serve
    print('Serving on http://127.0.0.1:8000')
    serve(app, host='127.0.0.1', port=8000, threads=100)
    

# if __name__ == "__main__":
#     # uvicorn.run(app, host="127.0.0.1", port=8000)
#     from wsgiref import simple_server
#     httpd = simple_server.make_server('127.0.0.1', 8000, app)
#     print('Serving on http://127.0.0.1:8000')
#     httpd.serve_forever()

# Test inputs
#https://www.linkedin.com/in/williamhgates/
#https://www.pravaahconsulting.com/
#https://calendly.com/pravaahconsulting/
#software development