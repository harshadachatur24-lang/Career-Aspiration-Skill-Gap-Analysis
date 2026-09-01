# ======================================================================
# CAREERPATH AI - COMPLETE REPLACEMENT APP
# Career Aspiration & Skill Gap Analysis System
# ======================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib
from pathlib import Path
import re

st.set_page_config(page_title="CareerPath AI", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

# ------------------------------ PATHS ---------------------------------
APP_DIR = Path(__file__).resolve().parent
possible_roots = [APP_DIR, APP_DIR.parent, APP_DIR.parent.parent]
PROJECT_ROOT = next((p for p in possible_roots if (p / "data").exists() or (p / "models").exists()), APP_DIR.parent)
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

# ------------------------------ STYLE ---------------------------------
st.markdown("""
<style>
.stApp { background:#f7f9fc; }
section[data-testid="stSidebar"] { background:#111827; }
section[data-testid="stSidebar"] * { color:white !important; }
.main-title { font-size:38px; font-weight:800; margin-bottom:4px; }
.subtitle { color:#64748b; font-size:16px; margin-bottom:22px; }
.section-title { font-size:25px; font-weight:750; margin-top:22px; margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)

CAREER_DOMAINS = {'Technology & Data': ['Data Analyst', 'Data Scientist', 'Data Engineer', 'Machine Learning Engineer', 'AI Engineer', 'Business Intelligence (BI) Analyst', 'BI Developer', 'Database Administrator (DBA)', 'Database Developer', 'Software Developer / Software Engineer', 'Web Developer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer', 'Mobile App Developer', 'Cloud Engineer', 'Cloud Architect', 'DevOps Engineer', 'MLOps Engineer', 'Cybersecurity Analyst', 'Cybersecurity Engineer', 'Network Engineer', 'System Administrator', 'QA / Software Testing Engineer', 'Automation Test Engineer', 'Data Visualization Specialist', 'NLP Engineer', 'Computer Vision Engineer', 'AI Research Scientist', 'Big Data Engineer', 'Data Architect', 'Solutions Architect', 'IT Business Analyst', 'IT Project Manager', 'Blockchain Developer', 'IoT Engineer', 'Robotics Engineer', 'Prompt Engineer / Generative AI Specialist', 'AI Product Manager', 'Technical Support Engineer'], 'Business & Management': ['Business Analyst', 'Management Consultant', 'Project Manager', 'Product Manager', 'Operations Manager', 'Business Development Manager', 'Human Resources (HR) Manager', 'Marketing Manager', 'Supply Chain Manager', 'Operations Analyst', 'Strategy Analyst', 'Management Analyst', 'Entrepreneur / Business Owner', 'Program Manager', 'Risk Manager', 'Sales Manager', 'Relationship Manager', 'Procurement Manager', 'Administrative Manager', 'General Manager'], 'Finance & Accounting': ['Financial Analyst', 'Accountant', 'Chartered Accountant (CA)', 'Investment Analyst', 'Financial Advisor', 'Auditor', 'Tax Consultant', 'Risk Analyst', 'Credit Analyst', 'Investment Banker', 'Financial Planner', 'Banking Officer', 'Treasury Analyst', 'Equity Research Analyst', 'Finance Manager'], 'Marketing & Media': ['Marketing Analyst', 'Digital Marketing Specialist', 'Marketing Manager', 'Social Media Manager', 'SEO Specialist', 'Content Strategist', 'Brand Manager', 'Market Research Analyst', 'Advertising Specialist', 'Public Relations (PR) Specialist', 'Copywriter', 'Content Creator', 'Media Planner', 'Communications Specialist', 'Growth Marketing Specialist'], 'Design & Creative': ['UI/UX Designer', 'Graphic Designer', 'Product Designer', 'Web Designer', 'Fashion Designer', 'Interior Designer', 'Animator', '3D Designer', 'Video Editor', 'Photographer', 'Illustrator', 'Art Director', 'Motion Graphics Designer', 'Creative Director', 'Visual Designer'], 'Education': ['School Teacher', 'College Professor', 'Lecturer', 'Educational Consultant', 'Curriculum Developer', 'Instructional Designer', 'Academic Counsellor', 'Education Administrator', 'Online Tutor', 'Corporate Trainer', 'Educational Content Developer', 'Learning & Development Specialist', 'Special Education Teacher', 'Education Researcher', 'School Administrator'], 'Science & Research': ['Research Scientist', 'Research Analyst', 'Biologist', 'Chemist', 'Physicist', 'Environmental Scientist', 'Microbiologist', 'Biotechnology Researcher', 'Data Research Scientist', 'Laboratory Scientist', 'Scientific Officer', 'Research Associate', 'Biomedical Researcher', 'Environmental Researcher', 'Scientific Data Analyst']}

SOFT_SKILLS = ['Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking', 'Time Management', 'Decision Making', 'Confidence', 'Presentation Skills']

TECHNOLOGY_SKILLS = {'Programming & Development': ['Python', 'Java', 'C++', 'JavaScript', 'Object-Oriented Programming (OOP)', 'Data Structures & Algorithms (DSA)'], 'Data & Analytics': ['SQL', 'Excel', 'Data Analysis', 'Statistics', 'Data Visualization', 'Power BI'], 'AI & Machine Learning': ['Machine Learning', 'Deep Learning', 'Artificial Intelligence', 'Natural Language Processing (NLP)', 'Computer Vision', 'Generative AI'], 'Database & Data Engineering': ['SQL', 'Database Management', 'Data Modeling', 'Data Warehousing', 'ETL', 'Apache Spark'], 'Cloud & Infrastructure': ['Cloud Computing', 'AWS', 'Microsoft Azure', 'Linux', 'Docker', 'Kubernetes'], 'Cybersecurity': ['Cybersecurity', 'Network Security', 'Information Security', 'Cryptography', 'SIEM', 'Threat Detection'], 'APIs & Integration': ['APIs', 'REST APIs', 'API Testing', 'Web3', 'IoT Protocols'], 'Testing & Quality': ['Software Testing', 'Test Automation', 'Test Case Design', 'Selenium', 'API Testing', 'SDLC'], 'Specialized Technology': ['Embedded Systems', 'Sensors', 'Internet of Things (IoT)', 'Robotics', 'ROS', 'Computer Vision'], 'Business, Product & Project': ['Business Analysis', 'Project Management', 'Product Management', 'Agile/Scrum', 'Requirements Gathering', 'Communication'], 'Professional & Research': ['Problem Solving', 'Critical Thinking', 'Analytical Thinking', 'Research Skills', 'Evaluation & Validation', 'Leadership']}

BUSINESS_SKILLS = ['Business Analysis', 'Project Management', 'Product Management', 'Operations Management', 'Business Development', 'Human Resource Management', 'Marketing Management', 'Supply Chain Management', 'Logistics', 'Inventory Management', 'Procurement', 'Data Analysis', 'Excel', 'SQL', 'Process Improvement', 'Reporting', 'Strategic Planning', 'Market Research', 'Leadership', 'Risk Management', 'Risk Assessment', 'Financial Analysis', 'Financial Management', 'Marketing', 'Sales', 'Decision Making', 'Program Management', 'Communication', 'Requirements Gathering', 'Negotiation', 'Presentation', 'Customer Relationship Management', 'Planning', 'Administration']

FINANCE_SKILLS = ['Financial Analysis', 'Excel', 'Financial Modeling', 'Accounting', 'Data Analysis', 'Financial Reporting', 'Bookkeeping', 'Taxation', 'Auditing', 'Compliance', 'Investment Analysis', 'Market Research', 'Valuation', 'Financial Planning', 'Risk Management', 'Communication', 'Client Relationship Management', 'Tax Planning', 'Risk Assessment', 'Statistics', 'Credit Analysis', 'Negotiation', 'Banking Operations', 'Customer Service', 'Treasury Management', 'Cash Management', 'Equity Research', 'Budgeting', 'Leadership', 'Strategic Planning', 'Research']

MARKETING_SKILLS = ['Data Analysis', 'Marketing Analytics', 'Excel', 'SQL', 'Market Research', 'Data Visualization', 'Digital Marketing', 'SEO', 'Social Media Marketing', 'Content Marketing', 'Google Ads', 'Analytics', 'Marketing Strategy', 'Brand Management', 'Leadership', 'Communication', 'Content Creation', 'Content Strategy', 'Social Media Analytics', 'Community Management', 'Keyword Research', 'Google Analytics', 'Content Optimization', 'Technical SEO', 'Link Building', 'Content Planning', 'Copywriting', 'Consumer Behavior', 'Campaign Management', 'Statistics', 'Survey Design', 'Advertising', 'Digital Advertising', 'Public Relations', 'Media Relations', 'Content Writing', 'Crisis Management', 'Networking', 'Creativity', 'Storytelling', 'Video Editing', 'Photography', 'Media Planning', 'Campaign Analytics', 'Budget Management', 'Presentation', 'A/B Testing', 'Growth Marketing']

DESIGN_SKILLS = ['UI Design', 'UX Design', 'Graphic Design', 'Product Design', 'Web Design', 'Fashion Design', 'Interior Design', 'Visual Design', 'Art Direction', 'Creative Strategy', 'Design Thinking', 'Branding', 'User Research', 'Wireframing', 'Prototyping', 'Space Planning', 'Storyboarding', 'Composition', 'Design Visualization', 'Typography', 'Color Theory', 'Sketching', 'Drawing', 'Digital Illustration', 'Creativity', 'Storytelling', 'Communication', 'Leadership', 'Figma', 'Adobe Photoshop', 'Adobe Illustrator', 'Adobe After Effects', 'Adobe Premiere Pro', 'Adobe Lightroom', 'AutoCAD', 'Blender', '2D Animation', '3D Animation', '3D Modeling', '3D Rendering', 'Texturing', 'Lighting', 'Motion Design', 'Motion Graphics', 'Video Editing', 'Color Grading', 'Character Design', 'Textile Design', 'Pattern Making']

EDUCATION_SKILLS = ['Teaching', 'Subject Knowledge', 'Lesson Planning', 'Classroom Management', 'Assessment', 'Student Engagement', 'Student Support', 'Online Teaching', 'Adult Learning', 'Learning Theory', 'Curriculum Development', 'Instructional Design', 'Assessment Design', 'Content Development', 'E-Learning', 'Educational Technology', 'Individualized Education Plans (IEP)', 'Research', 'Educational Research', 'Research Methodology', 'Data Analysis', 'Statistics', 'Academic Writing', 'Critical Thinking', 'Subject Expertise', 'Communication', 'Presentation', 'Counselling', 'Student Guidance', 'Career Counselling', 'Active Listening', 'Facilitation', 'Education Management', 'Administration', 'Leadership', 'Planning', 'Decision Making', 'Project Management', 'Budget Management', 'Performance Management', 'Digital Tools', 'Content Writing', 'Creativity', 'Training & Development']

SCIENCE_SKILLS = ['Scientific Research', 'Research Methodology', 'Scientific Analysis', 'Experimentation', 'Research Design', 'Field Research', 'Critical Thinking', 'Problem Solving', 'Observation', 'Data Analysis', 'Statistics', 'Data Visualization', 'Machine Learning', 'Python', 'SQL', 'Excel', 'Computational Modeling', 'Laboratory Techniques', 'Chemical Analysis', 'Safety Procedures', 'Documentation', 'Environmental Monitoring', 'Biology', 'Chemistry', 'Physics', 'Mathematics', 'Microbiology', 'Biotechnology', 'Molecular Biology', 'Environmental Science', 'Biomedical Science', 'Scientific Writing', 'Communication', 'Project Management']

CAREER_REQUIREMENTS = {'Data Analyst': ['SQL', 'Data Analysis', 'Statistics', 'Excel', 'Data Visualization', 'Power BI'], 'Data Scientist': ['Python', 'SQL', 'Statistics', 'Data Analysis', 'Machine Learning', 'Data Visualization'], 'Data Engineer': ['Python', 'SQL', 'Database Management', 'ETL', 'Data Warehousing', 'Apache Spark'], 'Machine Learning Engineer': ['Python', 'Machine Learning', 'Deep Learning', 'Data Structures & Algorithms (DSA)', 'SQL', 'Docker'], 'AI Engineer': ['Python', 'Artificial Intelligence', 'Machine Learning', 'Deep Learning', 'Generative AI', 'APIs'], 'Business Intelligence (BI) Analyst': ['SQL', 'Excel', 'Data Analysis', 'Data Visualization', 'Power BI', 'Statistics'], 'BI Developer': ['SQL', 'Data Warehousing', 'Data Modeling', 'ETL', 'Power BI', 'Data Visualization'], 'Database Administrator (DBA)': ['SQL', 'Database Management', 'Linux', 'Data Modeling', 'Data Warehousing', 'Information Security'], 'Database Developer': ['SQL', 'Database Management', 'Data Modeling', 'Python', 'ETL', 'Data Warehousing'], 'Software Developer / Software Engineer': ['Python', 'Java', 'C++', 'Object-Oriented Programming (OOP)', 'Data Structures & Algorithms (DSA)', 'Software Testing'], 'Web Developer': ['HTML/CSS', 'JavaScript', 'APIs', 'REST APIs', 'Software Testing', 'Git'], 'Frontend Developer': ['JavaScript', 'HTML/CSS', 'UI Design', 'APIs', 'REST APIs', 'Software Testing'], 'Backend Developer': ['Python', 'Java', 'SQL', 'APIs', 'REST APIs', 'Database Management'], 'Full Stack Developer': ['JavaScript', 'HTML/CSS', 'Python', 'SQL', 'APIs', 'Database Management'], 'Mobile App Developer': ['Java', 'Object-Oriented Programming (OOP)', 'Data Structures & Algorithms (DSA)', 'APIs', 'Software Testing', 'UI Design'], 'Cloud Engineer': ['Cloud Computing', 'AWS', 'Microsoft Azure', 'Linux', 'Docker', 'Kubernetes'], 'Cloud Architect': ['Cloud Computing', 'AWS', 'Microsoft Azure', 'Linux', 'Docker', 'Kubernetes'], 'DevOps Engineer': ['Linux', 'Docker', 'Kubernetes', 'Cloud Computing', 'AWS', 'SDLC'], 'MLOps Engineer': ['Python', 'Machine Learning', 'Docker', 'Kubernetes', 'Cloud Computing', 'AWS'], 'Cybersecurity Analyst': ['Cybersecurity', 'Network Security', 'Linux', 'SIEM', 'Threat Detection', 'Information Security'], 'Cybersecurity Engineer': ['Cybersecurity', 'Network Security', 'Information Security', 'Cryptography', 'Threat Detection', 'Linux'], 'Network Engineer': ['Network Security', 'Linux', 'Cybersecurity', 'Cloud Computing', 'APIs', 'Information Security'], 'System Administrator': ['Linux', 'Cloud Computing', 'Cybersecurity', 'Network Security', 'Docker', 'Information Security'], 'QA / Software Testing Engineer': ['Software Testing', 'Test Case Design', 'Test Automation', 'Selenium', 'API Testing', 'SDLC'], 'Automation Test Engineer': ['Test Automation', 'Selenium', 'Software Testing', 'API Testing', 'Test Case Design', 'SDLC'], 'Data Visualization Specialist': ['Data Visualization', 'Power BI', 'Data Analysis', 'Excel', 'SQL', 'Statistics'], 'NLP Engineer': ['Python', 'Natural Language Processing (NLP)', 'Machine Learning', 'Deep Learning', 'Artificial Intelligence', 'Generative AI'], 'Computer Vision Engineer': ['Python', 'Computer Vision', 'Machine Learning', 'Deep Learning', 'Artificial Intelligence', 'Data Analysis'], 'AI Research Scientist': ['Python', 'Artificial Intelligence', 'Machine Learning', 'Deep Learning', 'Research Skills', 'Statistics'], 'Big Data Engineer': ['Python', 'SQL', 'Apache Spark', 'ETL', 'Data Warehousing', 'Data Modeling'], 'Data Architect': ['SQL', 'Data Modeling', 'Data Warehousing', 'Database Management', 'ETL', 'Apache Spark'], 'Solutions Architect': ['Cloud Computing', 'AWS', 'Microsoft Azure', 'APIs', 'Database Management', 'System Design'], 'IT Business Analyst': ['Business Analysis', 'Requirements Gathering', 'Data Analysis', 'SQL', 'Communication', 'Problem Solving'], 'IT Project Manager': ['Project Management', 'Agile/Scrum', 'Leadership', 'Requirements Gathering', 'Communication', 'Risk Management'], 'Blockchain Developer': ['C++', 'JavaScript', 'Object-Oriented Programming (OOP)', 'Data Structures & Algorithms (DSA)', 'Web3', 'APIs'], 'IoT Engineer': ['Internet of Things (IoT)', 'Sensors', 'IoT Protocols', 'Python', 'Embedded Systems', 'APIs'], 'Robotics Engineer': ['Robotics', 'ROS', 'C++', 'Python', 'Computer Vision', 'Sensors'], 'Prompt Engineer / Generative AI Specialist': ['Generative AI', 'Artificial Intelligence', 'Natural Language Processing (NLP)', 'Python', 'Critical Thinking', 'Problem Solving'], 'AI Product Manager': ['Product Management', 'Artificial Intelligence', 'Machine Learning', 'Business Analysis', 'Communication', 'Leadership'], 'Technical Support Engineer': ['Linux', 'Networking', 'APIs', 'Problem Solving', 'Communication', 'Software Testing'], 'Business Analyst': ['Business Analysis', 'Data Analysis', 'Excel', 'SQL', 'Problem Solving', 'Communication'], 'Management Consultant': ['Business Analysis', 'Strategic Planning', 'Data Analysis', 'Market Research', 'Problem Solving', 'Presentation'], 'Project Manager': ['Project Management', 'Leadership', 'Communication', 'Planning', 'Risk Management', 'Decision Making'], 'Product Manager': ['Product Management', 'Business Analysis', 'Market Research', 'Strategic Planning', 'Communication', 'Leadership'], 'Operations Manager': ['Operations Management', 'Process Improvement', 'Planning', 'Data Analysis', 'Leadership', 'Decision Making'], 'Business Development Manager': ['Business Development', 'Sales', 'Negotiation', 'Communication', 'Market Research', 'Strategic Planning'], 'Human Resources (HR) Manager': ['Human Resource Management', 'Communication', 'Leadership', 'Decision Making', 'Planning', 'Conflict Management'], 'Marketing Manager': ['Marketing Strategy', 'Brand Management', 'Digital Marketing', 'Market Research', 'Leadership', 'Communication'], 'Supply Chain Manager': ['Supply Chain Management', 'Logistics', 'Inventory Management', 'Procurement', 'Data Analysis', 'Planning'], 'Operations Analyst': ['Data Analysis', 'Excel', 'SQL', 'Process Improvement', 'Problem Solving', 'Reporting'], 'Strategy Analyst': ['Strategic Planning', 'Data Analysis', 'Market Research', 'Business Analysis', 'Problem Solving', 'Presentation'], 'Management Analyst': ['Business Analysis', 'Data Analysis', 'Process Improvement', 'Problem Solving', 'Research', 'Communication'], 'Entrepreneur / Business Owner': ['Leadership', 'Business Strategy', 'Financial Management', 'Marketing', 'Sales', 'Decision Making'], 'Program Manager': ['Program Management', 'Project Management', 'Leadership', 'Risk Management', 'Communication', 'Strategic Planning'], 'Risk Manager': ['Risk Management', 'Risk Assessment', 'Data Analysis', 'Financial Analysis', 'Problem Solving', 'Decision Making'], 'Sales Manager': ['Sales', 'Communication', 'Negotiation', 'Leadership', 'Customer Relationship Management', 'Decision Making'], 'Relationship Manager': ['Customer Relationship Management', 'Communication', 'Negotiation', 'Sales', 'Customer Service', 'Problem Solving'], 'Procurement Manager': ['Procurement', 'Negotiation', 'Supply Chain Management', 'Inventory Management', 'Data Analysis', 'Planning'], 'Administrative Manager': ['Administration', 'Planning', 'Communication', 'Leadership', 'Budgeting', 'Decision Making'], 'General Manager': ['Leadership', 'Strategic Planning', 'Operations Management', 'Financial Management', 'Communication', 'Decision Making'], 'Financial Analyst': ['Financial Analysis', 'Excel', 'Financial Modeling', 'Accounting', 'Data Analysis', 'Financial Reporting'], 'Accountant': ['Accounting', 'Bookkeeping', 'Taxation', 'Financial Reporting', 'Excel', 'Auditing'], 'Chartered Accountant (CA)': ['Accounting', 'Auditing', 'Taxation', 'Financial Reporting', 'Financial Analysis', 'Compliance'], 'Investment Analyst': ['Financial Analysis', 'Investment Analysis', 'Financial Modeling', 'Excel', 'Market Research', 'Valuation'], 'Financial Advisor': ['Financial Planning', 'Investment Analysis', 'Risk Management', 'Communication', 'Client Relationship Management', 'Tax Planning'], 'Auditor': ['Auditing', 'Accounting', 'Risk Assessment', 'Financial Reporting', 'Compliance', 'Data Analysis'], 'Tax Consultant': ['Taxation', 'Accounting', 'Tax Planning', 'Compliance', 'Financial Analysis', 'Research'], 'Risk Analyst': ['Risk Management', 'Risk Assessment', 'Financial Analysis', 'Data Analysis', 'Statistics', 'Excel'], 'Credit Analyst': ['Credit Analysis', 'Financial Analysis', 'Risk Assessment', 'Accounting', 'Excel', 'Data Analysis'], 'Investment Banker': ['Financial Modeling', 'Valuation', 'Investment Analysis', 'Financial Analysis', 'Excel', 'Negotiation'], 'Financial Planner': ['Financial Planning', 'Investment Analysis', 'Risk Management', 'Tax Planning', 'Financial Analysis', 'Communication'], 'Banking Officer': ['Banking Operations', 'Accounting', 'Financial Analysis', 'Customer Service', 'Risk Management', 'Communication'], 'Treasury Analyst': ['Treasury Management', 'Cash Management', 'Financial Analysis', 'Risk Management', 'Excel', 'Financial Reporting'], 'Equity Research Analyst': ['Equity Research', 'Financial Analysis', 'Financial Modeling', 'Valuation', 'Market Research', 'Excel'], 'Finance Manager': ['Financial Management', 'Financial Analysis', 'Budgeting', 'Financial Reporting', 'Leadership', 'Strategic Planning'], 'Marketing Analyst': ['Data Analysis', 'Marketing Analytics', 'Excel', 'SQL', 'Market Research', 'Data Visualization'], 'Digital Marketing Specialist': ['Digital Marketing', 'SEO', 'Social Media Marketing', 'Content Marketing', 'Google Ads', 'Analytics'], 'Social Media Manager': ['Social Media Marketing', 'Content Creation', 'Content Strategy', 'Social Media Analytics', 'Communication', 'Community Management'], 'SEO Specialist': ['SEO', 'Keyword Research', 'Google Analytics', 'Content Optimization', 'Technical SEO', 'Link Building'], 'Content Strategist': ['Content Strategy', 'Content Marketing', 'Content Planning', 'SEO', 'Market Research', 'Copywriting'], 'Brand Manager': ['Brand Management', 'Marketing Strategy', 'Market Research', 'Consumer Behavior', 'Communication', 'Campaign Management'], 'Market Research Analyst': ['Market Research', 'Data Analysis', 'Statistics', 'Consumer Behavior', 'Survey Design', 'Data Visualization'], 'Advertising Specialist': ['Advertising', 'Digital Advertising', 'Campaign Management', 'Copywriting', 'Market Research', 'Analytics'], 'Public Relations (PR) Specialist': ['Public Relations', 'Communication', 'Media Relations', 'Content Writing', 'Crisis Management', 'Networking'], 'Copywriter': ['Copywriting', 'Content Writing', 'Creativity', 'SEO', 'Storytelling', 'Communication'], 'Content Creator': ['Content Creation', 'Video Editing', 'Photography', 'Social Media Marketing', 'Storytelling', 'Creativity'], 'Media Planner': ['Media Planning', 'Market Research', 'Advertising', 'Data Analysis', 'Campaign Analytics', 'Budget Management'], 'Communications Specialist': ['Communication', 'Content Writing', 'Public Relations', 'Media Relations', 'Presentation', 'Storytelling'], 'Growth Marketing Specialist': ['Growth Marketing', 'Digital Marketing', 'Data Analysis', 'A/B Testing', 'SEO', 'Marketing Analytics'], 'UI/UX Designer': ['UI Design', 'UX Design', 'User Research', 'Wireframing', 'Prototyping', 'Figma'], 'Graphic Designer': ['Graphic Design', 'Typography', 'Color Theory', 'Adobe Photoshop', 'Adobe Illustrator', 'Creativity'], 'Product Designer': ['Product Design', 'UX Design', 'UI Design', 'User Research', 'Prototyping', 'Design Thinking'], 'Web Designer': ['Web Design', 'UI Design', 'HTML/CSS', 'Responsive Design', 'Figma', 'Typography'], 'Fashion Designer': ['Fashion Design', 'Sketching', 'Textile Design', 'Color Theory', 'Pattern Making', 'Creativity'], 'Interior Designer': ['Interior Design', 'Space Planning', '3D Modeling', 'AutoCAD', 'Sketching', 'Color Theory'], 'Animator': ['2D Animation', '3D Animation', 'Storyboarding', 'Character Design', 'Motion Design', 'Adobe After Effects'], '3D Designer': ['3D Modeling', '3D Rendering', 'Texturing', 'Lighting', 'Blender', 'Design Visualization'], 'Video Editor': ['Video Editing', 'Adobe Premiere Pro', 'Adobe After Effects', 'Storytelling', 'Motion Graphics', 'Color Grading'], 'Photographer': ['Photography', 'Composition', 'Lighting', 'Photo Editing', 'Adobe Lightroom', 'Creativity'], 'Illustrator': ['Digital Illustration', 'Drawing', 'Sketching', 'Typography', 'Adobe Illustrator', 'Creativity'], 'Art Director': ['Art Direction', 'Creative Strategy', 'Leadership', 'Visual Design', 'Branding', 'Communication'], 'Motion Graphics Designer': ['Motion Graphics', 'Animation', 'Adobe After Effects', 'Adobe Premiere Pro', 'Typography', 'Visual Design'], 'Creative Director': ['Creative Strategy', 'Art Direction', 'Leadership', 'Branding', 'Communication', 'Design Thinking'], 'Visual Designer': ['Visual Design', 'Graphic Design', 'UI Design', 'Typography', 'Color Theory', 'Figma'], 'School Teacher': ['Teaching', 'Lesson Planning', 'Classroom Management', 'Communication', 'Subject Knowledge', 'Assessment'], 'College Professor': ['Teaching', 'Subject Expertise', 'Research', 'Academic Writing', 'Presentation', 'Communication'], 'Lecturer': ['Teaching', 'Subject Knowledge', 'Lesson Planning', 'Presentation', 'Communication', 'Assessment'], 'Educational Consultant': ['Education Consulting', 'Communication', 'Research', 'Problem Solving', 'Curriculum Development', 'Project Management'], 'Curriculum Developer': ['Curriculum Development', 'Instructional Design', 'Educational Research', 'Lesson Planning', 'Assessment Design', 'Content Development'], 'Instructional Designer': ['Instructional Design', 'E-Learning', 'Curriculum Development', 'Learning Theory', 'Content Development', 'Educational Technology'], 'Academic Counsellor': ['Counselling', 'Communication', 'Student Guidance', 'Career Counselling', 'Active Listening', 'Problem Solving'], 'Education Administrator': ['Education Management', 'Leadership', 'Administration', 'Communication', 'Planning', 'Decision Making'], 'Online Tutor': ['Online Teaching', 'Communication', 'Subject Knowledge', 'Digital Tools', 'Lesson Planning', 'Student Engagement'], 'Corporate Trainer': ['Training & Development', 'Communication', 'Presentation', 'Leadership', 'Facilitation', 'Adult Learning'], 'Educational Content Developer': ['Content Development', 'Content Writing', 'Subject Knowledge', 'Educational Technology', 'Creativity', 'Research'], 'Learning & Development Specialist': ['Learning & Development', 'Training', 'Instructional Design', 'Performance Management', 'Communication', 'Data Analysis'], 'Special Education Teacher': ['Special Education', 'Teaching', 'Classroom Management', 'Individualized Education Plans (IEP)', 'Communication', 'Student Support'], 'Education Researcher': ['Educational Research', 'Data Analysis', 'Statistics', 'Academic Writing', 'Research Methodology', 'Critical Thinking'], 'School Administrator': ['School Administration', 'Leadership', 'Planning', 'Communication', 'Budget Management', 'Decision Making'], 'Research Scientist': ['Research Methodology', 'Scientific Research', 'Data Analysis', 'Statistics', 'Scientific Writing', 'Critical Thinking'], 'Research Analyst': ['Data Analysis', 'Statistics', 'Research Methodology', 'Excel', 'Data Visualization', 'Critical Thinking'], 'Biologist': ['Biology', 'Laboratory Techniques', 'Scientific Research', 'Data Analysis', 'Scientific Writing', 'Observation'], 'Chemist': ['Chemistry', 'Laboratory Techniques', 'Chemical Analysis', 'Experimentation', 'Data Analysis', 'Safety Procedures'], 'Physicist': ['Physics', 'Mathematics', 'Data Analysis', 'Computational Modeling', 'Experimentation', 'Problem Solving'], 'Environmental Scientist': ['Environmental Science', 'Data Analysis', 'Environmental Monitoring', 'Statistics', 'Research Methodology', 'Field Research'], 'Microbiologist': ['Microbiology', 'Laboratory Techniques', 'Biotechnology', 'Experimentation', 'Data Analysis', 'Scientific Research'], 'Biotechnology Researcher': ['Biotechnology', 'Molecular Biology', 'Laboratory Techniques', 'Scientific Research', 'Data Analysis', 'Experimentation'], 'Data Research Scientist': ['Python', 'Statistics', 'Data Analysis', 'Machine Learning', 'Research Methodology', 'Data Visualization'], 'Laboratory Scientist': ['Laboratory Techniques', 'Experimentation', 'Scientific Analysis', 'Data Analysis', 'Safety Procedures', 'Documentation'], 'Scientific Officer': ['Scientific Research', 'Data Analysis', 'Research Methodology', 'Scientific Writing', 'Project Management', 'Communication'], 'Research Associate': ['Research Methodology', 'Data Analysis', 'Scientific Writing', 'Experimentation', 'Critical Thinking', 'Documentation'], 'Biomedical Researcher': ['Biomedical Science', 'Biology', 'Laboratory Techniques', 'Research Methodology', 'Data Analysis', 'Scientific Writing'], 'Environmental Researcher': ['Environmental Science', 'Environmental Research', 'Data Analysis', 'Field Research', 'Statistics', 'Scientific Writing'], 'Scientific Data Analyst': ['Data Analysis', 'Statistics', 'Python', 'SQL', 'Data Visualization', 'Machine Learning']}


# ======================================================================
# HELPERS / SESSION
# ======================================================================

def norm_skill(s):
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

def unique(seq):
    return list(dict.fromkeys(seq))

def career_domain(career):
    for d, careers in CAREER_DOMAINS.items():
        if career in careers:
            return d
    return "Other"

def score_status(current, required=5):
    gap = max(float(required) - float(current), 0)
    if gap == 0:
        return "✅ Strong / Ready"
    if gap == 1:
        return "🟡 Developing"
    if gap == 2:
        return "🟠 Needs Improvement"
    return "🔴 Skill Gap"

def readiness(match):
    if match >= 80: return "Ready"
    if match >= 60: return "Developing"
    return "Needs Development"

def build_assessment_map():
    # Keep the user's domain/sub-field structure, but remove duplicate sliders
    # such as SQL appearing in more than one Technology category.
    domain_structures = {
        "Technology & Data": TECHNOLOGY_SKILLS,
        "Business & Management": {"Core Business Skills": BUSINESS_SKILLS},
        "Finance & Accounting": {"Core Finance Skills": FINANCE_SKILLS},
        "Marketing & Media": {"Core Marketing Skills": MARKETING_SKILLS},
        "Design & Creative": {"Core Design Skills": DESIGN_SKILLS},
        "Education": {"Core Education Skills": EDUCATION_SKILLS},
        "Science & Research": {"Core Science Skills": SCIENCE_SKILLS},
    }
    return domain_structures

DOMAIN_STRUCTURES = build_assessment_map()

# Add any career requirement that is not present in the domain master list.
# This prevents a required skill from silently becoming score 0 just because
# its spelling/category was missing from the assessment list.
for domain, careers in CAREER_DOMAINS.items():
    existing = set()
    for vals in DOMAIN_STRUCTURES[domain].values():
        existing.update(norm_skill(x) for x in vals)
    extras = []
    for career in careers:
        for skill in CAREER_REQUIREMENTS.get(career, []):
            if norm_skill(skill) not in existing and skill not in SOFT_SKILLS:
                extras.append(skill)
                existing.add(norm_skill(skill))
    if extras:
        DOMAIN_STRUCTURES[domain]["Career-specific Skills"] = unique(extras)

# Normalized requirement lookup.
REQUIREMENT_LOOKUP = {
    career: unique(reqs) for career, reqs in CAREER_REQUIREMENTS.items()
}

if "student_profile" not in st.session_state:
    st.session_state.student_profile = None
if "student_skills" not in st.session_state:
    st.session_state.student_skills = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

def recommend_careers(student_skills):
    # Deterministic skill-matching engine. Every required skill contributes
    # equally to the career match; no career is selected by the student.
    scores = []
    normalized_student = {norm_skill(k): float(v) for k, v in student_skills.items()}
    for career, requirements in REQUIREMENT_LOOKUP.items():
        if not requirements:
            continue
        vals = []
        assessed = 0
        for skill in requirements:
            key = norm_skill(skill)
            if key in normalized_student:
                value = max(0.0, min(5.0, normalized_student[key]))
                assessed += 1
            else:
                # Missing/unknown skill is treated as unassessed, not as a
                # fake zero. It is still shown as a gap later.
                value = 0.0
            vals.append(value)
        match = (sum(vals) / (5.0 * len(requirements))) * 100.0
        coverage = (assessed / len(requirements)) * 100.0
        scores.append({
            "Career": career,
            "Domain": career_domain(career),
            "Match": round(match, 1),
            "Skill_Coverage": round(coverage, 1),
            "Readiness": readiness(match),
        })
    df = pd.DataFrame(scores).sort_values(["Match", "Skill_Coverage", "Career"], ascending=[False, False, True]).reset_index(drop=True)
    df["Rank"] = np.arange(1, len(df) + 1)
    return df[["Rank", "Career", "Domain", "Match", "Skill_Coverage", "Readiness"]]

# --------------------------- NAVIGATION --------------------------------
st.sidebar.markdown("## 🎯 CareerPath AI")
st.sidebar.caption("Career Aspiration & Skill Gap Analysis")
page = st.sidebar.radio("Navigation", [
    "🏠 Home", "📝 Student Assessment", "🎯 Career Recommendations",
    "🧩 Skill Gap Analysis", "📚 Development Plan", "🔎 Career Explorer",
    "📊 Project Analytics"
])
st.sidebar.markdown("---")
st.sidebar.caption("7 Career Domains")
for d in CAREER_DOMAINS:
    st.sidebar.caption(f"• {d}")

# ======================================================================
# HOME
# ======================================================================
if page == "🏠 Home":
    st.markdown('<div class="main-title">🎯 CareerPath AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Career Aspiration & Skill Gap Analysis System</div>', unsafe_allow_html=True)
    st.info("Complete the Student Assessment. You do not select a career first — your assessed skills are compared with career requirements automatically.")
    total_careers = sum(len(x) for x in CAREER_DOMAINS.values())
    c1, c2, c3 = st.columns(3)
    c1.metric("Career Domains", len(CAREER_DOMAINS))
    c2.metric("Career Options", total_careers)
    c3.metric("Compulsory Soft Skills", len(SOFT_SKILLS))
    st.markdown('<div class="section-title">How CareerPath AI Works</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for col, text in zip(cols, ["01\n\nStudent Profile", "02\n\nSkill Assessment", "03\n\nCareer Matching", "04\n\nTop Career Recommendations", "05\n\nSkill Gap & Development Plan"]):
        col.info(text)
    st.markdown('<div class="section-title">7 Career Domains</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (domain, careers) in enumerate(CAREER_DOMAINS.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"### {domain}")
                st.write(f"{len(careers)} career options")

# ======================================================================
# STUDENT ASSESSMENT
# ======================================================================
elif page == "📝 Student Assessment":
    st.markdown('<div class="main-title">📝 Student Skill Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Name is optional. Soft skills are compulsory. Rate every shown skill from 0–5; the system will recommend careers automatically.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">👤 Basic Profile</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        student_name = st.text_input("Student Name (Optional)", placeholder="Enter your name if you want it shown in your results")
        age = st.number_input("Age", min_value=15, max_value=60, value=20, step=1)
        degree_options = ["B.Sc.", "B.Com.", "B.A.", "B.E. / B.Tech", "BBA", "BCA", "M.Sc.", "M.Com.", "M.A.", "MBA", "MCA", "Other"]
        degree = st.selectbox("Degree", degree_options)
        if degree == "Other":
            degree = st.text_input("Enter Degree")
    with b:
        cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
        internships = st.number_input("Internships", min_value=0, max_value=20, value=0, step=1)
        projects = st.number_input("Projects", min_value=0, max_value=30, value=0, step=1)
        certifications = st.number_input("Certifications", min_value=0, max_value=30, value=0, step=1)

    branch_options = ["Data Science", "Computer Science", "Information Technology", "Artificial Intelligence / ML", "Computer Engineering", "Electronics", "Mechanical", "Civil", "Commerce", "Accounting & Finance", "Management", "Marketing", "Arts / Humanities", "Science", "Biotechnology", "Physics", "Chemistry", "Mathematics", "Education", "Design", "Other"]
    branch = st.selectbox("Branch / Specialization", branch_options)
    if branch == "Other":
        branch = st.text_input("Enter Branch / Specialization")
    st.caption("Tip: choose the closest standard degree and specialization. Use ‘Other’ only when your actual degree/branch is not listed.")

    st.markdown('<div class="section-title">🧠 Compulsory Soft Skills</div>', unsafe_allow_html=True)
    st.info("These soft skills are common and useful across all career domains. All are required in the assessment.")
    soft_scores = {}
    soft_cols = st.columns(2)
    for i, skill in enumerate(SOFT_SKILLS):
        with soft_cols[i % 2]:
            soft_scores[skill] = st.slider(f"{skill}", 1, 5, 3, key=f"soft_{i}")

    st.markdown('<div class="section-title">💻 Domain Skill Assessment</div>', unsafe_allow_html=True)
    st.write("You do not choose a career. Rate the skills you actually have. The same scores are used by recommendation, skill-gap and development pages.")
    domain_scores = {}
    for domain, categories in DOMAIN_STRUCTURES.items():
        with st.expander(f"🔹 {domain}", expanded=False):
            for category, skills in categories.items():
                st.markdown(f"**{category}**")
                clean_skills = [s for s in unique(skills) if s not in SOFT_SKILLS]
                cols = st.columns(3)
                for i, skill in enumerate(clean_skills):
                    key = norm_skill(skill)
                    # One widget per normalized skill, even if it appears in multiple categories.
                    if key in domain_scores:
                        continue
                    with cols[i % 3]:
                        domain_scores[key] = st.slider(skill, 0, 5, 0, key=f"skill_{key.replace(' ', '_').replace('/', '_')}")

    if st.button("🚀 Generate Career Recommendations", type="primary", use_container_width=True):
        student_skills = dict(soft_scores)
        # Convert normalized keys back to a readable canonical name for display.
        canonical = {}
        for domain, categories in DOMAIN_STRUCTURES.items():
            for skills in categories.values():
                for skill in skills:
                    canonical[norm_skill(skill)] = skill
        for k, v in domain_scores.items():
            student_skills[canonical.get(k, k)] = v
        profile = {"Name": student_name.strip(), "Age": age, "Degree": degree, "Branch": branch, "CGPA": cgpa, "Internships": internships, "Projects": projects, "Certifications": certifications}
        recommendations = recommend_careers(student_skills)
        st.session_state.student_profile = profile
        st.session_state.student_skills = student_skills
        st.session_state.recommendations = recommendations
        st.success("Assessment completed successfully. Your recommendations are ready.")
        if student_name.strip():
            st.info(f"Results prepared for **{student_name.strip()}**. Open 🎯 Career Recommendations from the sidebar.")
        else:
            st.info("Open 🎯 Career Recommendations from the sidebar.")

# ======================================================================
# CAREER RECOMMENDATIONS
# ======================================================================
elif page == "🎯 Career Recommendations":
    st.markdown('<div class="main-title">🎯 Career Recommendations</div>', unsafe_allow_html=True)
    recs = st.session_state.recommendations
    profile = st.session_state.student_profile
    if recs is None:
        st.warning("Please complete the Student Assessment first.")
        st.stop()
    if profile and profile.get("Name"):
        st.markdown(f"### Welcome, {profile['Name']} 👋")
    st.markdown('<div class="subtitle">Your careers are ranked automatically from your assessed skill scores.</div>', unsafe_allow_html=True)
    top5 = recs.head(5)
    st.markdown('<div class="section-title">🏆 Your Top 5 Career Matches</div>', unsafe_allow_html=True)
    for _, row in top5.iterrows():
        rank = int(row.Rank)
        medal = {1:"🥇",2:"🥈",3:"🥉"}.get(rank, f"#{rank}")
        with st.container(border=True):
            st.markdown(f"### {medal} {row.Career}")
            st.caption(row.Domain)
            c1, c2, c3 = st.columns(3)
            c1.metric("Match", f"{row.Match:.1f}%")
            c2.metric("Skill Coverage", f"{row.Skill_Coverage:.1f}%")
            c3.metric("Readiness", row.Readiness)
    chart_df = top5[["Career", "Match"]].copy()
    fig = px.bar(chart_df, x="Career", y="Match", text="Match", title="Top 5 Career Match Comparison")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(template="plotly_white", yaxis_title="Match (%)", yaxis_range=[0,100])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="section-title">📋 Other Career Matches</div>', unsafe_allow_html=True)
    st.caption("Showing the next 15 ranked careers. Total available careers: 134.")
    rest = recs.iloc[5:20].copy()
    rest.columns = ["Rank", "Career", "Domain", "Match %", "Skill Coverage %", "Readiness"]
    st.dataframe(rest, use_container_width=True, hide_index=True)

# ======================================================================
# SKILL GAP ANALYSIS
# ======================================================================
elif page == "🧩 Skill Gap Analysis":
    st.markdown('<div class="main-title">🧩 Skill Gap Analysis</div>', unsafe_allow_html=True)
    recs = st.session_state.recommendations
    student_skills = st.session_state.student_skills
    if recs is None or student_skills is None:
        st.warning("Please complete the Student Assessment first.")
        st.stop()
    selected_career = st.selectbox("Select a recommended career to inspect its skill gaps", recs.head(10)["Career"].tolist())
    requirements = REQUIREMENT_LOOKUP[selected_career]
    normalized = {norm_skill(k): float(v) for k, v in student_skills.items()}
    rows = []
    for skill in requirements:
        current = normalized.get(norm_skill(skill), 0.0)
        required = 5.0
        gap = max(required-current, 0.0)
        rows.append({"Skill": skill, "My Score": current, "Required": required, "Gap": gap, "Status": score_status(current, required)})
    gap_df = pd.DataFrame(rows)
    strong = int((gap_df["Gap"] == 0).sum())
    developing = int(((gap_df["Gap"] > 0) & (gap_df["Gap"] <= 2)).sum())
    gaps = int((gap_df["Gap"] > 2).sum())
    c1,c2,c3 = st.columns(3)
    c1.metric("Strong Skills", strong)
    c2.metric("Developing Skills", developing)
    c3.metric("Skill Gaps", gaps)
    st.markdown(f"### 🎯 {selected_career}")
    st.caption(career_domain(selected_career))
    show_df = gap_df.copy()
    show_df["My Score"] = show_df["My Score"].map(lambda x: f"{x:.0f}/5")
    show_df["Required"] = show_df["Required"].map(lambda x: f"{x:.0f}/5")
    show_df["Gap"] = show_df["Gap"].map(lambda x: f"{x:.0f}")
    st.markdown("### Required Skills vs My Skills")
    st.dataframe(show_df, use_container_width=True, hide_index=True)
    chart_gap = gap_df[gap_df.Gap > 0].sort_values("Gap", ascending=True)
    if not chart_gap.empty:
        fig = px.bar(chart_gap, x="Gap", y="Skill", orientation="h", title=f"Skill Gaps — {selected_career}")
        fig.update_layout(template="plotly_white", height=max(350, 45*len(chart_gap)))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("Excellent! You currently meet the required level for all assessed skills in this career.")

# ======================================================================
# DEVELOPMENT PLAN
# ======================================================================
elif page == "📚 Development Plan":
    st.markdown('<div class="main-title">📚 Personalized Development Plan</div>', unsafe_allow_html=True)
    recs = st.session_state.recommendations
    student_skills = st.session_state.student_skills
    if recs is None or student_skills is None:
        st.warning("Please complete the Student Assessment first.")
        st.stop()
    selected_career = st.selectbox("Career", recs.head(10)["Career"].tolist(), key="development_career")
    normalized = {norm_skill(k): float(v) for k, v in student_skills.items()}
    rows = []
    for skill in REQUIREMENT_LOOKUP[selected_career]:
        current = normalized.get(norm_skill(skill), 0.0)
        target = 5.0
        gap = max(target-current, 0.0)
        if gap == 0: priority = "None — Strong"
        elif gap == 1: priority = "Low"
        elif gap == 2: priority = "Medium"
        else: priority = "High"
        rows.append({"Skill": skill, "Current": current, "Target": target, "Gap": gap, "Priority": priority, "Status": score_status(current,target)})
    development_df = pd.DataFrame(rows).sort_values(["Gap", "Skill"], ascending=[False, True]).reset_index(drop=True)
    st.markdown(f"### 🎯 {selected_career}")
    st.markdown("### 🔥 High Priority Skills")
    high = development_df[development_df.Priority == "High"]
    if high.empty:
        st.success("No high-priority skills for this career.")
    else:
        for _, row in high.iterrows():
            with st.container(border=True):
                st.markdown(f"### 📚 {row.Skill}")
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Current", f"{row.Current:.0f}/5")
                c2.metric("Target", f"{row.Target:.0f}/5")
                c3.metric("Gap", f"{row.Gap:.0f}")
                c4.metric("Priority", row.Priority)
                st.write("Focus on structured learning, practical exercises, projects and real-world application.")
    st.markdown("### 📋 Development Roadmap")
    roadmap = development_df.copy()
    roadmap["Current"] = roadmap["Current"].map(lambda x: f"{x:.0f}/5")
    roadmap["Target"] = roadmap["Target"].map(lambda x: f"{x:.0f}/5")
    roadmap["Gap"] = roadmap["Gap"].map(lambda x: f"{x:.0f}")
    st.dataframe(roadmap, use_container_width=True, hide_index=True)

# ======================================================================
# CAREER EXPLORER
# ======================================================================
elif page == "🔎 Career Explorer":
    st.markdown('<div class="main-title">🔎 Career Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Explore the 7 domains, careers and required core skills.</div>', unsafe_allow_html=True)
    selected_domain = st.selectbox("Select Career Domain", list(CAREER_DOMAINS.keys()))
    selected_career = st.selectbox("Select Career", CAREER_DOMAINS[selected_domain])
    requirements = REQUIREMENT_LOOKUP.get(selected_career, [])
    with st.container(border=True):
        st.markdown(f"### 🎯 {selected_career}")
        st.caption(selected_domain)
        st.write(f"**Required core skills:** {len(requirements)}")
    st.markdown("### 🛠️ Required Core Skills")
    cols = st.columns(3)
    for i, skill in enumerate(requirements):
        cols[i % 3].write(f"• {skill}")

# ======================================================================
# PROJECT ANALYTICS - USE EXISTING PKL FILES ONLY
# ======================================================================
elif page == "📊 Project Analytics":
    st.markdown('<div class="main-title">📊 Project Analytics</div>', unsafe_allow_html=True)
    ranking_path = DATA_DIR / "final_career_ranking.pkl"
    summary_path = DATA_DIR / "final_student_career_summary.pkl"
    gaps_path = DATA_DIR / "final_skill_gaps.pkl"
    if not ranking_path.exists():
        st.info("Existing project analytics files were not found. This does not affect the new-student assessment and recommendation engine.")
    else:
        ranking = pd.read_pickle(ranking_path)
        summary = pd.read_pickle(summary_path) if summary_path.exists() else None
        gaps = pd.read_pickle(gaps_path) if gaps_path.exists() else None
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Students", f"{summary['Student_ID'].nunique():,}" if summary is not None and 'Student_ID' in summary.columns else "—")
        c2.metric("Careers", ranking['Career'].nunique() if 'Career' in ranking.columns else "—")
        c3.metric("Career Records", f"{len(ranking):,}")
        c4.metric("Skill Gap Records", f"{len(gaps):,}" if gaps is not None else "—")
        if 'Career' in ranking.columns:
            counts = ranking['Career'].value_counts().head(15).reset_index()
            counts.columns = ['Career','Students']
            st.plotly_chart(px.bar(counts, x='Career', y='Students', title='Most Recommended Careers'), use_container_width=True)
        if 'Domain' in ranking.columns:
            dom = ranking.groupby('Domain')['Student_ID'].nunique().reset_index()
            dom.columns = ['Domain','Students']
            st.plotly_chart(px.pie(dom, names='Domain', values='Students', title='Career Domain Distribution'), use_container_width=True)

# ======================================================================
# FOOTER
# ======================================================================
st.markdown("---")
st.caption("🎯 CareerPath AI • Career Aspiration & Skill Gap Analysis System • Python • Pandas • Machine Learning • Streamlit")