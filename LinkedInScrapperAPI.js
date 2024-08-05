//importing the node packages
const express = require('express');
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

//instantiating the express
const app= express();
//defining the port 
const PORT = 8600;

// function for fetching the linkedin profile data
async function getProfile(handle){
    try{
    const res =await fetch(`https://www.linkedin.com/voyager/api/identity/profiles/${handle}/profileView`, 
        {
    "headers": {
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
      "Referer": `https://www.linkedin.com/in/${handle}/`,
      "Referrer-Policy": "strict-origin-when-cross-origin"
    },
    "body": null,
    "method": "GET"
  });
  const data = await res.json();

    const entityWithAllTheData = data?.included?.find(
      (d) => d?.publicIdentifier && d?.publicIdentifier !== ""
    );
    // course details 
    const courses = data?.included?.filter(
        (d) => d?.$type === 'com.linkedin.voyager.identity.profile.Course'
      );
    // school details  
    const school_names = data?.included?.filter(
      (d) => d?.$type == "com.linkedin.voyager.entities.shared.MiniSchool"
    )
    
    //education details
    const education = data?.included?.filter(
      (d) => d?.$type == "com.linkedin.voyager.identity.profile.Education"
    )
    // experience details
    const experience =data?.included?.filter(
      (d) => d?.$type == "com.linkedin.voyager.identity.profile.Position"
    )

    //linkedin profile summary
    const profile_summary = data?.included.find(
      (d) => d?.$type =="com.linkedin.voyager.identity.profile.Profile"
    )

    //returning the profile details
    return {
      firstName: entityWithAllTheData?.firstName,
      lastName: entityWithAllTheData?.lastName,
      // headline: entityWithAllTheData?.headline,
      currentOccupation: entityWithAllTheData?.occupation,
      aboutSection: profile_summary?.summary,
      country: profile_summary?.geoCountryName,
      city: profile_summary?.geoLocationName,
      handle: entityWithAllTheData?.publicIdentifier,
      url: `https://www.linkedin.com/in/${entityWithAllTheData?.publicIdentifier}/`,
      // publicIdentifier: entityWithAllTheData?.publicIdentifier,
      //profileId: thingWithProfileId?.report?.authorProfileId,
      courseNames : courses.map((course) => course.name),
      schools: school_names.map((school) => school.schoolName),
      schoolDetails: education.map((details)=> ['schoolName: '+ details?.schoolName,'degreeName: '+ details.degreeName, 'fiedlOfStudy: '+details.fieldOfStudy,'startDate: '+ details.timePeriod?.startDate?.year, 'endDate: '+ details.timePeriod?.endDate?.year]),
      experienceDetails: experience.map((details)=> ['company: '+details?.companyName, 'description: '+details.description, 'location: '+details.geoLocationName, 'title: '+details.title,'startDate: '+ 'month: '+details.timePeriod?.startDate?.month + ' year: '+ details.timePeriod?.startDate?.year, 'endDate: '+ 'month: ' +details.timePeriod?.endDate?.month + ' year: '+ details.timePeriod?.endDate?.year])
    };
  } catch (error) {
    console.log("error at topProfile", error.message);
  }
}
//testing in console
// getProfile('williamhgates').then(function(result) {
//     console.log(result); // "normalReturn"
//   });

// api route to fetch the data from the linkedin profile by passing the profile handle
app.get('/profile/:handle', async (req, res) => {
  const handle = req.params.handle;
  try {
    // calling getProfile function here
    const profileData = await getProfile(handle);
    res.json(profileData);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching profile data' });
  }
});


app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});


  