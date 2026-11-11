"""Localized content, scam dictionaries, advisory tips, and simulation scripts."""

LANGS = {
    "Hindi / Hinglish": "hi-IN",
    "Marathi": "mr-IN",
    "English (India)": "en-IN",
}

# (regex_pattern, weight, readable_label, scam_type_key)
RULES = [
    (r"digital arrest|डिजिटल अरेस्ट|डिजिटल अटक", 40, "Digital arrest threat", "arrest"),
    (r"cbi|ed officer|police|crime branch|cyber crime|पुलिस|सीबीआई|सीबीआय|पोलीस|सायबर क्राईम", 15, "Impersonating authority", "arrest"),
    (r"otp|ओटीपी|\bpin\b|cvv|पिन", 30, "Asks for OTP/PIN/CVV", "otp"),
    (r"kyc|केवाईसी|केवायसी|account.{0,15}(block|band|बंद)|खात[ाे].{0,10}(बंद|ब्लॉक)", 35, "Fake KYC / account block", "kyc"),
    (r"anydesk|teamviewer|rustdesk|quicksupport|screen share|एनीडेस्क", 30, "Remote-access app request", "remote"),
    (r"arrest|गिरफ्तार|अटक|warrant|वारंट", 20, "Arrest/warrant threat", "arrest"),
    (r"parcel|courier|customs|fedex|पार्सल|कूरियर|कस्टम", 25, "Parcel/customs scam", "parcel"),
    (r"lottery|inam|इनाम|लॉटरी|prize|cashback|पुरस्कार", 20, "Prize/lottery bait", "prize"),
    (r"transfer|ट्रांसफर|पैसे भेज|पैसे पाठव|upi|यूपीआई|gift card|bitcoin|खाते में डालो", 20, "Pushes money transfer", "payment"),
    (r"abhi|turant|अभी|तुरंत|लगेच|urgent|immediately|24 hours|किसी को मत बता|kisi ko mat bata|कोणाला सांगू नका|do not tell anyone", 15, "Urgency / secrecy pressure", None),
]

TYPES = {
    "arrest": (
        "Digital Arrest / Fake Officer",
        {
            "hi-IN": "कोई भी सरकारी एजेंसी फोन या वीडियो कॉल पर 'डिजिटल अरेस्ट' नहीं करती। तुरंत कॉल काट दें।",
            "mr-IN": "कोणतीही सरकारी यंत्रणा फोनवर 'डिजिटल अरेस्ट' करत नाही. ताबडतोब कॉल कट करा.",
            "en-IN": "No law enforcement agency arrests anyone over phone or video call. Hang up immediately.",
        },
    ),
    "kyc": (
        "Fake KYC / Account Block",
        {
            "hi-IN": "बैंक कभी फोन पर KYC अपडेट या खाता बंद करने की धमकी नहीं देता। आधिकारिक बैंक ऐप या ब्रांच में ही संपर्क करें।",
            "mr-IN": "बँक फोनवर KYC अपडेट किंवा खाते बंद करण्याची धमकी देत नाही. बँकेच्या अधिकृत शाखेत चौकशी करा.",
            "en-IN": "Banks never threaten account suspension over a phone call. Check via official banking apps or branch.",
        },
    ),
    "otp": (
        "OTP / PIN Fraud",
        {
            "hi-IN": "OTP, PIN या CVV किसी के साथ साझा न करें, चाहे कॉलर खुद को बैंक अधिकारी ही क्यों न बताए।",
            "mr-IN": "OTP, PIN किंवा CVV कोणालाही सांगू नका, कॉलर बँकेचा अधिकारी असला तरीही नाही.",
            "en-IN": "Never share OTP, PIN, or CVV with anyone, even if the caller claims to be a bank official.",
        },
    ),
    "remote": (
        "Remote Access Scam",
        {
            "hi-IN": "AnyDesk, TeamViewer या QuickSupport इंस्टॉल न करें। इससे जालसाज आपके पूरे फोन का नियंत्रण ले लेते हैं।",
            "mr-IN": "AnyDesk किंवा TeamViewer सारखे ॲप्स इन्स्टॉल करू नका. यामुळे भामटे तुमच्या फोनचा ताबा घेतात.",
            "en-IN": "Do not install AnyDesk or TeamViewer. Attackers can view your screen and steal credentials.",
        },
    ),
    "parcel": (
        "Parcel / Customs Scam",
        {
            "hi-IN": "कथित कस्टम ड्यूटी या अवैध पार्सल के लिए पैसे न भेजें। कूरियर कंपनी से सीधे स्वयं जांच करें।",
            "mr-IN": "कस्टम शुल्क किंवा पार्सलच्या नावाखाली पैसे पाठवू नका. थेट कुरिअर कंपनीशी संपर्क साधा.",
            "en-IN": "Do not pay supposed customs fees on calls. Directly verify with courier support.",
        },
    ),
    "prize": (
        "Lottery / Prize Scam",
        {
            "hi-IN": "जिस लॉटरी या प्रतियोगिता में आपने भाग नहीं लिया, वह आप नहीं जीत सकते। पहले शुल्क मांगना ठगी है।",
            "mr-IN": "सहभाग न घेतलेली लॉटरी तुम्ही जिंकू शकत नाही. बक्षीस मिळवण्यासाठी आधी शुल्क मागणे ही शुद्ध फसवणूक आहे.",
            "en-IN": "You cannot win a lottery you never entered. Demanding upfront fees is always fraud.",
        },
    ),
    "payment": (
        "Money Transfer Pressure",
        {
            "hi-IN": "अपरिचित कॉलर के दबाव में किसी भी खाते या UPI पर पैसे ट्रांसफर न करें।",
            "mr-IN": "अनोळखी कॉलरच्या दबावाखाली कोणत्याही UPI किंवा बँक खात्यावर पैसे पाठवू नका.",
            "en-IN": "Never send UPI payments or wire transfers under pressure from an unknown caller.",
        },
    ),
}

WARNINGS = {
    "hi-IN": "सावधान! यह कॉल एक स्कैम हो सकती है। अपना ओटीपी, पिन या पैसे किसी को न दें और तुरंत कॉल काट दें। साइबर हेल्पलाइन 1930 पर शिकायत करें।",
    "mr-IN": "सावध राहा! हा कॉल फसवणूक असू शकतो. ओटीपी, पिन किंवा पैसे कोणालाही देऊ नका आणि ताबडतोब कॉल कट करा. सायबर हेल्पलाइन 1930 वर संपर्क करा.",
    "en-IN": "Warning! This call is very likely a scam. Do not share your OTP or send money. Hang up immediately and call helpline 1930.",
}

SAFE = {
    "hi-IN": "इस बातचीत में कोई स्पष्ट खतरा नहीं मिला, लेकिन फिर भी किसी अनजान व्यक्ति से ओटीपी या पासवर्ड साझा न करें।",
    "mr-IN": "या संभाषणात कोणताही धोका आढळला नाही, तरीही अनोळखी व्यक्तीसोबत ओटीपी किंवा पासवर्ड शेअर करू नका.",
    "en-IN": "No red flags detected in this conversation. However, never share passwords or OTPs with unknown callers.",
}

SHARE = {
    "hi-IN": "⚠️ स्कैम अलर्ट: मुझे अभी '{t}' प्रकार का संदिग्ध कॉल आया। किसी को भी OTP/PIN न दें और तुरंत कॉल काटें। राष्ट्रीय साइबर हेल्पलाइन: 1930",
    "mr-IN": "⚠️ स्कॅम अलर्ट: मला नुकताच '{t}' प्रकारचा फसवणूक कॉल आला होता. OTP/PIN कोणालाही देऊ नका. सायबर हेल्पलाइन: 1930",
    "en-IN": "⚠️ Scam Alert: I just received a suspicious '{t}' call. Never share OTP/PIN. Hang up immediately. Cyber helpline: 1930",
}

# Pre-packaged text samples (no audio needed) for quick demo
SAMPLES = {
    "— Pick a pre-loaded sample —": "",
    "Hinglish: Digital Arrest": "Main CBI Crime Branch se bol raha hoon, aapka digital arrest warrant nikla hai. Turant OTP verify karo aur kisi ko mat batana.",
    "Hindi: Fake Bank KYC": "आपका बैंक खाता 2 घंटे में बंद हो जाएगा। केवाईसी तुरंत अपडेट करने के लिए अपना ओटीपी और पिन बताइए।",
    "Marathi: Customs Parcel": "तुमच्या नावावर कस्टममध्ये अवैध पार्सल आले आहे. अटकेपासून वाचण्यासाठी लगेच यूपीआयने पैसे पाठवा आणि कोणाला सांगू नका.",
    "English: Remote AnyDesk Support": "This is official bank support. Your account is compromised. Please install AnyDesk immediately and share the connection code.",
    "Hindi: Safe Conversation": "नमस्ते रमेश जी, कल दोपहर 3 बजे प्रोजेक्ट मीटिंग है। कृपया समय पर आएं। धन्यवाद।",
}

# Simulator call scripts for Gnani Timbre TTS (at least 3 diverse scripts per language)
SCRIPTS = {
    "hi-IN": [
        (
            "Digital Arrest (CBI / Drugs Parcel)",
            "नमस्ते, मैं सीबीआई क्राइम ब्रांच से अधिकारी विजय बोल रहा हूँ। आपके आधार कार्ड से लिंक पार्सल में अवैध दवाइयां मिली हैं। आपका डिजिटल अरेस्ट हो चुका है। अभी अपना ओटीपी बताइए और किसी को मत बताइए।",
            "hi-IN",
        ),
        (
            "Fake Bank KYC (Account Suspension)",
            "प्रिय ग्राहक, आपका बैंक खाता आज शाम ब्लॉक कर दिया जाएगा। अपनी केवाईसी प्रक्रिया तुरंत पूरी करने के लिए बैंक सर्वर से भेजा गया ओटीपी और कार्ड पिन बताइए।",
            "hi-IN",
        ),
        (
            "Hinglish: CBI Digital Arrest",
            "Hello, main CBI crime branch officer Sharma bol raha hoon. Aapke naam par digital arrest warrant issue hua hai. Turant OTP confirm karo aur kisi ko mat batana.",
            "hi-en",
        ),
        (
            "Lottery / Prize Bait",
            "बधाई हो! आपने 25 लाख रुपये की राष्ट्रीय लॉटरी और कार जीती है। पुरस्कार राशि प्राप्त करने के लिए तुरंत 5000 रुपये रजिस्ट्रेशन फीस यूपीआई पर ट्रांसफर करें।",
            "hi-IN",
        ),
    ],
    "mr-IN": [
        (
            "Customs Parcel Threat",
            "नमस्कार, मी मुंबई कस्टम विभागातून बोलत आहे. तुमच्या नावावर आलेले एक पार्सल जप्त करण्यात आले आहे. अटक वॉरंट टाळण्यासाठी लगेच यूपीआयने पैसे पाठवा आणि कोणाला सांगू नका.",
            "mr-IN",
        ),
        (
            "Fake KYC Account Suspension",
            "तुमचे बँक खाते आज रात्री १२ वाजता कायमचे बंद होणार आहे. खात्याचे केवायसी अपडेट करण्यासाठी लगेच आलेला ओटीपी आणि पिन सांगा.",
            "mr-IN",
        ),
        (
            "Remote Screen Sharing Fraud",
            "मी बँकेच्या तांत्रिक विभागातून बोलत आहे. तुमच्या खात्यावर संशयास्पद व्यवहार सुरू आहेत. सुरक्षिततेसाठी मोबाईलमध्ये लगेच एनीडेस्क ॲप सुरू करा.",
            "mr-IN",
        ),
    ],
    "en-IN": [
        (
            "Digital Arrest Authority Threat",
            "This is Inspector Verma from Crime Branch. An arrest warrant is active under your name. Your digital arrest is in progress. Verify your OTP immediately and do not disconnect or inform anyone.",
            "en-IN",
        ),
        (
            "Remote Access AnyDesk Scam",
            "Good day, this is technical security regarding your banking account. Malicious activity is detected. Install AnyDesk screen share right now so we can stop the transaction.",
            "en-IN",
        ),
        (
            "Bank OTP Verification Trap",
            "Your debit card is under risk of termination. To restore privileges, please read out the 6-digit OTP sent to your registered mobile immediately.",
            "en-IN",
        ),
    ],
}

