from app.core.database import SessionLocal
from app.models.document import Document
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

model = SentenceTransformer("all-MiniLM-L6-v2")


def add_btc_hospital_data():
    db = SessionLocal()

    logger.info("=" * 80)
    logger.info("ADDING BTC HOSPITAL BOSTON - COMPLETE HOSPITAL DATA")
    logger.info("=" * 80)

    try:
        count = db.query(Document).count()
        logger.info(f"Found {count} existing documents")

        db.query(Document).delete()
        db.commit()
        logger.info("Documents cleared")
    except Exception:
        logger.exception("Failed to clear documents")
        db.rollback()
        db.close()
        return

    documents = [
        # ═══════════════════════════════════════════════════════
        # HOSPITAL INFORMATION
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Boston is a world-class medical institution located at 1500 Massachusetts Avenue, Boston, MA 02138, USA. Founded in 2010, BTC Hospital has established itself as a leader in healthcare with state-of-the-art facilities and compassionate patient care.",

        "BTC Hospital Boston features 250 beds including 45 ICU beds, 12 operation theaters, advanced diagnostic centers, 24/7 emergency department, in-house pharmacy, and specialized nursing staff trained in international standards.",

        "Our hospital is accredited by The Joint Commission (TJC), holds CAP certification for laboratory services, and is certified by the American College of Surgeons Commission on Cancer (CoC).",

        "Hospital address: 1500 Massachusetts Avenue, Boston, MA 02138. Contact: +1-617-555-0100. Email: info@btchospital.com. Website: www.btchospital.com",

        "Parking facilities available with 500 spaces. Free WiFi throughout hospital. Patient cafeteria with healthy food options. 24-hour gift shop and pharmacy.",

        # ═══════════════════════════════════════════════════════
        # CARDIOLOGY DEPARTMENT
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Cardiology Department is led by Dr. Michael Anderson, MD, FACC with 25 years of experience in interventional cardiology. He has performed over 8000 successful angioplasty procedures and specializes in complex coronary interventions.",

        "Cardiology consultation fee: $250 for first visit, $150 for follow-up appointment. Emergency cardiac consultation available 24/7 for $350.",

        "ECG (Electrocardiogram) test costs $200. 2D Echocardiography costs $450. Stress test (TMT) costs $650. Holter monitoring (24-hour) costs $500.",

        "Cardiac catheterization procedure costs $4500 to $6500. Coronary angioplasty with stent costs $8500 to $12000. Pacemaker implantation costs $22000 to $28000.",

        "Cardiology department operates Monday to Friday 8 AM to 6 PM, Saturday 9 AM to 2 PM. Emergency services available 24/7 with on-call cardiologist.",

        "Advanced cardiac equipment: Siemens Artis Zee Cath Lab with 3D imaging, GE Vivid E95 Echocardiography machines (3 units), Philips IntelliSpace ECG system.",

        "Cardiac rehabilitation program: 12-week program costing $1200 includes supervised exercise, nutrition counseling, and stress management. Available Tuesday to Thursday.",

        # ═══════════════════════════════════════════════════════
        # NEUROLOGY DEPARTMENT
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Neurology Department headed by Dr. Sarah Chen, MD, PhD with specialization in stroke management and neurovascular diseases. Experience of 18 years with 5000+ patient consultations.",

        "Neurology consultation fee: $275 for initial assessment, $175 for follow-up. Specialized consultations (stroke, epilepsy) available at $325.",

        "EEG (Electroencephalogram) test costs $300. MRI brain costs $1200. CT brain scan costs $600. Lumbar puncture procedure costs $400.",

        "Stroke treatment protocol: CT angiography $800 + thrombolytic therapy $3500 + hospitalization $1000-1500 per day.",

        "Epilepsy management program: Comprehensive evaluation $1500 + medication management $200 per consultation + EEG monitoring $500.",

        "Neurosurgery available: Craniotomy $25000-35000, Spinal fusion $18000-28000, Tumor removal $22000-32000 (depending on complexity).",

        # ═══════════════════════════════════════════════════════
        # ORTHOPEDIC DEPARTMENT
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Orthopedic Surgery Department directed by Dr. James Wilson, MD, FAAOS. Specializes in joint replacement, sports medicine, and trauma surgery with 22 years experience.",

        "Orthopedic consultation fee: $225 for new patient, $125 for follow-up. Sports medicine consultation available at $200.",

        "X-ray imaging costs $150. MRI joint scan costs $900. CT scan costs $700. Ultrasound costs $250.",

        "Total knee replacement surgery costs $28000-35000. Total hip replacement costs $32000-40000. Arthroscopic surgery costs $5000-8000.",

        "ACL reconstruction costs $12000-15000. Rotator cuff repair costs $8000-12000. Meniscus repair costs $6000-9000.",

        "Orthopedic rehabilitation program: 8-week program $1500 with physical therapy 3 times per week, includes home exercise program.",

        "Spine surgery available: Lumbar laminectomy $15000-18000, Spinal fusion $18000-25000, Discectomy $10000-13000.",

        # ═══════════════════════════════════════════════════════
        # ONCOLOGY DEPARTMENT
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Cancer Center provides comprehensive cancer care under direction of Dr. Patricia Lee, MD, PhD, Oncologist with 20 years cancer research and treatment experience.",

        "Oncology consultation fee: $300 for comprehensive cancer evaluation, $200 for follow-up. Second opinion consultation available at $400.",

        "Cancer screening: Mammography $350, Colonoscopy $1200, PSA test $150, Pap smear $200.",

        "Chemotherapy costs: $1500-3000 per cycle depending on drug regimen. Most cancers require 4-6 cycles.",

        "Radiation therapy: Initial planning $2000, treatment per session $500, typical course 25-30 sessions totaling $12500-15000.",

        "Surgical oncology: Breast cancer surgery $8000-12000, Colorectal cancer surgery $12000-16000, Lung cancer surgery $15000-20000.",

        "Tumor markers and genetic testing: Basic panel $800, Comprehensive genomic testing $2500-4000.",

        "Cancer support services: Free counseling, support groups, nutrition counseling, survivorship programs available to all cancer patients.",

        # ═══════════════════════════════════════════════════════
        # GASTROENTEROLOGY DEPARTMENT
        # ═══════════════════════════════════════════════════════

        "Gastroenterology Department led by Dr. Robert Martinez, MD, FACG. Specializes in endoscopic procedures, inflammatory bowel disease, and hepatology.",

        "GI consultation fee: $250 for new patient, $150 for established patient.",

        "Endoscopy procedure costs $1500. Colonoscopy costs $1800. Endoscopic ultrasound costs $2000.",

        "ERCP (Endoscopic Retrograde Cholangiopancreatography) costs $2500. Capsule endoscopy costs $1200.",

        "Liver biopsy costs $800. Abdominal ultrasound costs $300. CT abdomen costs $700.",

        "GI surgery available: Appendectomy $6000-8000, Cholecystectomy (gallbladder removal) $8000-10000, Hernia repair $5000-7000.",

        "IBD management program: Initial evaluation $400, ongoing management $200 per visit, biologics $2000-5000 per month.",

        # ═══════════════════════════════════════════════════════
        # PULMONOLOGY & RESPIRATORY DISEASE
        # ═══════════════════════════════════════════════════════

        "Pulmonology Department directed by Dr. Jennifer Brown, MD, FCCP with expertise in asthma, COPD, pulmonary hypertension, and interstitial lung disease.",

        "Pulmonology consultation fee: $225 for initial visit, $125 for follow-up.",

        "Spirometry (lung function test) costs $200. Chest X-ray costs $150. High-resolution CT chest costs $900.",

        "Bronchoscopy costs $1500. Transbronchial biopsy costs $2000. Pulmonary function tests costs $300.",

        "Sleep apnea diagnosis: Sleep study costs $1500, CPAP setup and training costs $1200.",

        "Asthma management program: Initial assessment $300, monthly follow-ups $150, includes medications and asthma action plan.",

        # ═══════════════════════════════════════════════════════
        # OBSTETRICS & GYNECOLOGY
        # ═══════════════════════════════════════════════════════

        "OB/GYN Department offers comprehensive women's healthcare led by Dr. Elizabeth Thompson, MD, FACOG with 19 years experience in obstetrics and gynecology.",

        "OB/GYN consultation fee: $225 for new patient, $125 for follow-up. Pregnancy consultation fee: $175.",

        "Prenatal care package: $2500 for 10 visits including ultrasounds, monitoring, and delivery support.",

        "Obstetric ultrasound: First trimester $300, Second/Third trimester $350, Detailed anatomy scan $400.",

        "Normal vaginal delivery costs $8000-10000 including hospital stay and postpartum care.",

        "Cesarean section (C-section) costs $12000-15000 including all hospital charges and recovery.",

        "Gynecologic procedures: Hysterectomy $8000-10000, Myomectomy (fibroid removal) $6000-8000, Laparoscopic surgery $5000-7000.",

        "Fertility services available: Initial consultation $350, Fertility testing $1200-2000, IVF treatment $12000-15000 per cycle.",

        # ═══════════════════════════════════════════════════════
        # PEDIATRICS
        # ═══════════════════════════════════════════════════════

        "Pediatrics Department provides comprehensive child healthcare under direction of Dr. David Kumar, MD, FAAP with specialization in pediatric infectious diseases.",

        "Pediatric consultation fee: $150 for well-child visit, $175 for sick child visit.",

        "Well-child screening includes developmental assessment, immunizations, and growth monitoring.",

        "Vaccination programs: Routine childhood immunizations $150 per visit, Special vaccines available including rotavirus, pneumococcal, HPV.",

        "Pediatric emergency care available 24/7. Pediatric ICU beds: 8 beds with specialized equipment for neonates and children.",

        "Neonatal care: Level III NICU with 15 beds, specialized care for premature and sick newborns, costs $2000-3000 per day.",

        # ═══════════════════════════════════════════════════════
        # DERMATOLOGY
        # ═══════════════════════════════════════════════════════

        "Dermatology Department led by Dr. Amanda Foster, MD, FAAD specializing in medical dermatology, cosmetic procedures, and dermatologic surgery.",

        "Dermatology consultation fee: $200 for new patient, $100 for follow-up. Cosmetic consultation fee: $300.",

        "Skin biopsy costs $350. Mohs micrographic surgery costs $1500-3000 per stage. Laser treatment costs $400-1000 per session.",

        "Acne treatment program: Initial evaluation $200, prescription medications $100-300, laser therapy (if needed) $800 per session.",

        "Melanoma screening: Full body skin exam $250. Dermoscopy available for suspicious lesions at $150.",

        "Cosmetic procedures: Botox injection $350 per area, Dermal fillers $500-800 per syringe, Laser hair removal $200-500 per session.",

        # ═══════════════════════════════════════════════════════
        # PSYCHIATRY & MENTAL HEALTH
        # ═══════════════════════════════════════════════════════

        "Psychiatry Department offers comprehensive mental health services under direction of Dr. Thomas White, MD, DFAPA with 21 years experience.",

        "Psychiatric consultation fee: $275 for initial evaluation, $175 for follow-up medication management.",

        "Therapy sessions: Individual therapy $150-200 per hour, Group therapy $60 per hour, Family therapy $200-250 per hour.",

        "Depression treatment: Initial assessment $300, medication management $150 per visit, psychotherapy additional.",

        "Anxiety disorders program: Evaluation $300, CBT (Cognitive Behavioral Therapy) $175 per session, Medication management $150 per visit.",

        "ADHD evaluation: Comprehensive assessment $400, Medication optimization $150 per visit, Behavioral coaching $100 per session.",

        "Substance abuse treatment: Detoxification program $3000-5000, Inpatient rehabilitation $15000-25000 per month, Outpatient program $2000 per month.",

        "Crisis intervention available 24/7. Psychiatric hospitalization: $1500-2000 per day for acute care.",

        # ═══════════════════════════════════════════════════════
        # EMERGENCY DEPARTMENT
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Emergency Department is fully staffed 24/7 with board-certified emergency physicians, trauma surgeons, and critical care specialists.",

        "Emergency room visit costs: $500 for triage and evaluation, additional costs for procedures and imaging.",

        "Trauma center status: Level II Trauma Center capable of handling major trauma cases with dedicated trauma team 24/7.",

        "Ambulance service: Basic life support $400, Advanced life support $600, Air ambulance available for long-distance transfers ($3000-5000).",

        "Fast track urgent care: Available for minor injuries and illnesses, costs $300-400, average wait time 15-20 minutes.",

        "CT scan in emergency: Head CT $600, Chest CT $700, Abdomen/Pelvis CT $800.",

        "Acute care surgery available: Emergency appendectomy $6000, Acute abdomen evaluation and surgery $8000-12000.",

        # ═══════════════════════════════════════════════════════
        # INTENSIVE CARE UNIT
        # ═══════════════════════════════════════════════════════

        "BTC Hospital operates two ICUs: Medical ICU (20 beds) and Surgical ICU (25 beds) with advanced monitoring and life support equipment.",

        "ICU daily charges: $2500 per day for bed and basic care. Additional charges for procedures, medications, and specialist consultations.",

        "Mechanical ventilation: $300 per day in addition to ICU charges.",

        "Continuous cardiac monitoring: Included in ICU charges.",

        "Central line placement: $400. Arterial line placement: $300. Dialysis (if needed): $1500-2000 per session.",

        "ECMO (Extracorporeal Membrane Oxygenation) available for critical patients: $5000 per day.",

        # ═══════════════════════════════════════════════════════
        # DIAGNOSTIC SERVICES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Diagnostic Center operates from 7 AM to 9 PM daily with latest imaging technology and rapid turnaround times.",

        "X-ray imaging: Chest $150, Abdomen $150, Extremities $100, Spine $200.",

        "Ultrasound: Abdomen $300, Obstetric $350, Cardiac echo $450, Vascular $400, Thyroid $250.",

        "CT scanning: Head $600, Chest $700, Abdomen/Pelvis $800, Spine $700, CTA (angiography) $1000.",

        "MRI scanning: Brain $1200, Spine $1100, Abdomen $1300, Extremities $900, MRA (angiography) $1400.",

        "PET-CT scanning: Standard $2500, Oncology PET-CT $2800.",

        "Mammography: Standard 2D $350, 3D tomosynthesis $500, Ultrasound guided biopsy $600.",

        "DEXA (Bone density) scan costs $250.",

        # ═══════════════════════════════════════════════════════
        # LABORATORY SERVICES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Laboratory Services provide rapid turnaround with state-of-the-art equipment. Results available same-day for routine tests.",

        "Complete Blood Count (CBC) costs $50. Comprehensive Metabolic Panel (CMP) costs $75. Lipid panel costs $60.",

        "Thyroid function tests (TSH, T3, T4) costs $100. Liver function tests costs $80. Kidney function tests costs $70.",

        "Blood glucose testing: Fasting $30, Random $25, Glucose tolerance test $100, HbA1c $60.",

        "Cardiac biomarkers: Troponin $150, BNP $200, High-sensitivity troponin $250.",

        "Blood cultures: $100 per set. Urinalysis: $40. Urine culture: $70.",

        "Coagulation studies: PT/INR $50, PTT $50, Full coagulation panel $150.",

        "Tumor markers: PSA $80, CEA $90, CA 19-9 $100, Cancer screening panel $500.",

        "Blood bank services: Type and cross $50, Packed RBC transfusion $300 per unit.",

        # ═══════════════════════════════════════════════════════
        # SURGICAL SERVICES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital operating rooms: 12 ORs with advanced equipment. Anesthesia services available 24/7 with board-certified anesthesiologists.",

        "Surgical costs include: Surgeon fee $3000-8000, Anesthesia $1500-3000, OR facility $2000-4000, Equipment/supplies $1000-3000, Hospital stay additional.",

        "General surgery procedures: Appendectomy $6000-8000, Cholecystectomy $8000-10000, Hernia repair $5000-7000, Colostomy $10000-12000.",

        "Vascular surgery: Carotid endarterectomy $12000-15000, AAA repair $25000-35000, Limb bypass $15000-20000.",

        "Thoracic surgery: Lung resection $20000-25000, Chest wall surgery $15000-18000.",

        "Colorectal surgery: Colectomy $12000-15000, Rectal surgery $14000-18000.",

        "Bariatric surgery: Gastric bypass $18000-22000, Gastric sleeve $16000-20000, LAP-BAND $12000-15000.",

        # ═══════════════════════════════════════════════════════
        # REHABILITATION SERVICES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Rehabilitation Department provides inpatient and outpatient services for post-operative recovery and chronic conditions.",

        "Physical therapy session costs $150 per hour. Typical recovery requires 2-3 sessions per week.",

        "Occupational therapy costs $150 per hour. Speech therapy costs $150 per hour.",

        "Post-stroke rehabilitation program: 4-week intensive program $4000 including PT, OT, speech therapy, and psychosocial support.",

        "Cardiac rehabilitation: 12-week supervised program $1200 with exercise monitoring and education.",

        "Orthopedic rehabilitation: 8-week program $1500 following joint surgery with progressive strengthening.",

        "Inpatient rehabilitation: $2000 per day for comprehensive rehabilitation services in specialized unit.",

        # ═══════════════════════════════════════════════════════
        # PHARMACY SERVICES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital In-House Pharmacy operates 24/7 providing all medications including specialty and oncology drugs.",

        "Prescription medications: Generic $15-50, Brand name $50-200 depending on medication.",

        "Specialty medications: Biologics $2000-10000 per month, Oncology drugs $1000-5000 per dose.",

        "IV medications: Infusion costs $200-500 depending on medication type and infusion time.",

        "Medication counseling: Free consultation by pharmacist available at point of dispensing.",

        "Pharmacy refill service: Same-day refills available. Home delivery service available for chronic medications.",

        # ═══════════════════════════════════════════════════════
        # HOSPITAL ACCOMMODATIONS
        # ═══════════════════════════════════════════════════════

        "BTC Hospital offers various room types: General ward $600 per day, Semi-private room $1000 per day, Private room $1500 per day.",

        "All rooms include: 24-hour nursing care, TV with cable, telephone, WiFi, private bathroom, comfortable bedding.",

        "Suite accommodations available: Deluxe suite with sitting area $2000 per day, Presidential suite with kitchen $2500 per day.",

        "Accommodation includes: Three meals per day, visiting hours 8 AM to 8 PM, 24-hour room service for limited items.",

        "Maternity package: Private delivery room $2000, Recovery room $1500 per day, Rooming-in facility for mother and baby.",

        # ═══════════════════════════════════════════════════════
        # HEALTH PACKAGES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Basic Health Checkup Package costs $500 including physical examination, basic blood tests, and health consultation.",

        "BTC Hospital Comprehensive Health Checkup Package costs $1500 including all basic tests, advanced imaging, specialist consultations, and personalized health report.",

        "BTC Hospital Executive Health Package costs $3500 including comprehensive assessment, advanced imaging (MRI/CT), specialist evaluations, and 1-year follow-up.",

        "Cardiac Health Package costs $2000 including ECG, echocardiography, stress test, cardiac biomarkers, and cardiologist consultation.",

        "Diabetic Health Package costs $1500 including glucose monitoring, kidney function tests, eye exam, foot screening, and endocrinologist consultation.",

        "Women's Health Package costs $1800 including gynecologic exam, mammography, pap smear, ultrasound, and women's health counseling.",

        "Men's Health Package costs $1600 including PSA screening, cardiac evaluation, prostate exam, and men's health counseling.",

        "Senior Citizen Package (65+) costs $2200 including comprehensive assessment, bone density scan, cognitive testing, and geriatric medicine consultation.",

        "Couples Health Package costs $2500 for two people including comprehensive checkups and joint health counseling.",

        "Cancer Screening Package costs $2800 including tumor markers, imaging, and oncology consultation.",

        # ═══════════════════════════════════════════════════════
        # VACCINATION SERVICES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Vaccination Center offers all routine and special vaccinations for children and adults.",

        "Routine childhood vaccines: Each dose $100, Series typically 10-12 vaccines by age 18.",

        "Adult routine vaccines: Flu $40, Pneumonia $150, Tdap $50, Shingles (Shingrix) $200 (2 doses).",

        "Travel vaccines: Yellow fever $150, Typhoid $120, Hepatitis A $100, Japanese encephalitis $180, Rabies series $300.",

        "HPV vaccine series (Gardasil 9): $300 per dose, 2-3 doses required based on age.",

        "COVID-19 vaccines: Available free or low cost depending on insurance.",

        # ═══════════════════════════════════════════════════════
        # DENTAL SERVICES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Dental Clinic provides preventive and restorative dental care. Dental consultation fee: $150.",

        "Teeth cleaning (prophylaxis) costs $120 per visit. Fluoride treatment additional $50.",

        "Filling: Amalgam $200 per tooth, Composite $300 per tooth.",

        "Root canal treatment costs $1000-1500 per tooth. Crown and bridge costs $500-800 per unit.",

        "Tooth extraction: Simple $300-400, Surgical $500-600.",

        "Orthodontic treatment (braces): Initial consultation $200, Treatment costs $4000-6000 for 18-24 months.",

        # ═══════════════════════════════════════════════════════
        # SPECIAL SERVICES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital offers telemedicine consultations: $150 per consultation with video visit to any available specialist.",

        "Home health services available: Nursing visit $200, Physical therapy at home $150 per session.",

        "Medical certificate issuance: $100 for general certificate, $150 for fitness-to-travel certificate.",

        "Health counseling services available: Nutrition counseling $100 per session, Smoking cessation program $200, Weight management program $300.",

        "Hospital transportation: Wheelchair accessible transport $50, Stretcher service $75.",

        # ═══════════════════════════════════════════════════════
        # INSURANCE & PAYMENT
        # ═══════════════════════════════════════════════════════

        "BTC Hospital accepts all major health insurance plans including Blue Cross Blue Shield, Aetna, Cigna, UnitedHealth, Humana.",

        "In-network insurance: Patients pay copay, coinsurance, deductible. Out-of-network: Insurance covers 60-70%, patient responsibility 30-40%.",

        "Payment methods accepted: Cash, Credit card (Visa, Mastercard, American Express), Debit card, Bank transfer, Installment plans available.",

        "Medicare accepted for patients 65+. Medicaid accepted for eligible patients. Workers' compensation accepted.",

        "Emergency care payment: Bill issued within 2 weeks. Payment plans available for amounts over $5000.",

        "Medical loans available through CareCreditProgram: 0% APR for 6-12 months depending on loan amount.",

        "Self-pay discounts: 10% discount for full payment within 30 days, 5% discount for payment within 60 days.",

        # ═══════════════════════════════════════════════════════
        # APPOINTMENT SCHEDULING
        # ═══════════════════════════════════════════════════════

        "Online appointment booking available 24/7 at www.btchospital.com. Phone appointments: Monday-Friday 8 AM to 6 PM at +1-617-555-0100.",

        "Walk-in patients accepted: General clinic hours Monday-Friday 9 AM to 5 PM. Emergency 24/7.",

        "Average waiting time: Scheduled appointment 10-15 minutes, Walk-in 30-60 minutes depending on volume.",

        "Appointment cancellation: Free cancellation up to 24 hours before appointment.",

        "Video consultation available: Same-day appointments possible for telemedicine consultations.",

        "Priority appointments: Senior citizens (65+), Pregnant women, Critical patients, Emergency cases.",

        # ═══════════════════════════════════════════════════════
        # HOSPITAL TIMINGS
        # ═══════════════════════════════════════════════════════

        "OPD (Outpatient Department): Monday-Friday 9 AM to 5 PM, Saturday 9 AM to 1 PM, Sunday Closed (Emergency open).",

        "Emergency Department: 24/7 open all days including holidays.",

        "Diagnostic Center: 7 AM to 9 PM Monday-Saturday, 9 AM to 5 PM Sunday.",

        "Laboratory: 7 AM to 6 PM daily, Express results within 4 hours.",

        "Pharmacy: 24/7 operation, In-patient and emergency medications always available.",

        "Visiting hours: General ward 10 AM to 4 PM and 6 PM to 8 PM, Pediatric ward 10 AM to 8 PM, ICU restricted visiting with special permission.",

        # ═══════════════════════════════════════════════════════
        # PATIENT SERVICES
        # ═══════════════════════════════════════════════════════

        "BTC Hospital patient services include: Language interpretation (20+ languages), Medical records request service, Patient advocate office.",

        "Hospital cafeteria: Open 6 AM to 8 PM serving breakfast, lunch, dinner, and snacks. Catering services available for patient meals.",

        "Chaplain services: Interfaith chaplain available for spiritual counseling and support.",

        "Patient education programs: Free classes on diabetes management, cardiac health, cancer support, parenting skills.",

        "Support groups: Cancer survivors, Cardiac patients, Mental health, Addiction recovery. Meetings twice weekly.",

        "Volunteer program: Volunteers assist patients with information, directions, and emotional support.",

        # ═══════════════════════════════════════════════════════
        # SPECIAL PROGRAMS
        # ═══════════════════════════════════════════════════════

        "BTC Hospital Diabetes Management Program: 6-week intensive program $1000 including education, meal planning, exercise program.",

        "Bariatric surgery program: Comprehensive evaluation $500, Surgery $18000-22000, 12-month follow-up included.",

        "Fertility and Infertility Program: Initial consultation $350, Fertility testing $1200-2000, IVF treatment $12000-15000 per cycle.",

        "Maternal-fetal medicine: Prenatal diagnosis $800, Fetal medicine consultation $400, High-risk pregnancy management available.",

        "Cardiac prevention program: Risk assessment $300, 12-week lifestyle modification $1200.",

        "Addiction medicine program: Detoxification $3000-5000, Rehabilitation $15000-25000 per month, Outpatient program $2000 per month.",

        # ═══════════════════════════════════════════════════════
        # RESEARCH & CLINICAL TRIALS
        # ═══════════════════════════════════════════════════════

        "BTC Hospital conducts clinical research in oncology, cardiology, neurology, and infectious diseases.",

        "Eligible patients may participate in clinical trials which may reduce or eliminate treatment costs.",

        "Research participation is voluntary and free. Patients can discuss eligibility with their treating physician.",

        "Informed consent required for all clinical trial participation with detailed information about risks and benefits.",

        # ═══════════════════════════════════════════════════════
        # QUALITY & ACCREDITATION
        # ═══════════════════════════════════════════════════════

        "BTC Hospital is accredited by The Joint Commission with Gold Seal of Approval demonstrating commitment to quality and safety.",

        "Hospital maintains 99.2% patient safety rating and 98.5% patient satisfaction score.",

        "All physicians are board-certified in their respective specialties with continuing medical education.",

        "Hospital employs 500+ healthcare professionals including 150+ physicians across all specialties.",

        "State-of-the-art infection control protocols implemented with monthly audits.",

        "Electronic health records system ensures privacy and security of patient information.",
    ]

    logger.info("Generating embeddings...")
    embeddings = model.encode(documents, show_progress_bar=True)

    for i, (content, embedding) in enumerate(zip(documents, embeddings), start=1):
        try:
            doc = Document(
                content=content,
                embedding=embedding.tolist()
            )
            db.add(doc)
            logger.info(f"Inserted document {i}")
        except Exception:
            logger.exception(f"Failed on document {i}")
            db.rollback()
            db.close()
            return

    db.commit()
    db.close()

    logger.info("=" * 80)
    logger.info(f"BTC HOSPITAL BOSTON DATABASE COMPLETE - {len(documents)} DOCUMENTS ADDED")
    logger.info("=" * 80)
    logger.info(f"Total documents: {len(documents)}")
    logger.info(
        f"Departments covered: Cardiology, Neurology, Orthopedics, Oncology, Gastroenterology, Pulmonology, OB/GYN, Pediatrics, Dermatology, Psychiatry")
    logger.info(
        f"Services covered: Consultation, Diagnostic tests, Surgeries, Rehabilitation, Pharmacy, Insurance, Appointments")
    logger.info(f"Database ready for RAG implementation")


if __name__ == "__main__":
    confirm = input("Type YES to add BTC Hospital Boston data: ").strip()
    if confirm == "YES":
        add_btc_hospital_data()
    else:
        print("Cancelled.")