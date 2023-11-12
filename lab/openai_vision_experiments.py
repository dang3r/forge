from openai import OpenAI

from pydantic import BaseModel
import instructor
#client = instructor.patch(OpenAI())
client = OpenAI()


class VolparaHealthScorecard(BaseModel):
    volumetric_breast_density_pct: float
    risk_score_pct: float
    risk_score_category: str

    volume_of_fibroglandular_tissue_cm3_right: float
    breast_volume_cm3_right: float
    volumetric_breast_density_pct_right: float

    volume_of_fibroglandular_tissue_cm3_left: float
    breast_volume_cm3_left: float
    volumetric_breast_density_pct_left: float

    patient_id: str
    patient_name: str
    patient_dob: str
    accession_number: str
    study_date: str

    udi: str
    version: str


v = VolparaHealthScorecard.model_json_schema()
print(v)
sc = client.chat.completions.create(
    model="gpt-4-vision-preview",
    max_tokens=600,
    #response_model=VolparaHealthScorecard,
    messages=[
    {
            "role": "user",
            "content": [
                {"type": "text", "text": f"""Extract the following from the
                                          image and return it as json:
    volumetric_breast_density_pct: float
    risk_score_pct: float
    risk_score_category: str

    volume_of_fibroglandular_tissue_cm3_right: float
    breast_volume_cm3_right: float
    volumetric_breast_density_pct_right: float

    volume_of_fibroglandular_tissue_cm3_left: float
    breast_volume_cm3_left: float
    volumetric_breast_density_pct_left: float

    patient_id: str
    patient_name: str
    patient_dob: str
    accession_number: str
    study_date: str

    udi: str
    version: str
                 """},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://i.ibb.co/mzM7Gqz/volparahealth.png"
                    },
                },
            ],
        }
    ]
)
resp  = sc.choices[0].message.content.split("```")[1][4:]
print(resp)
# convert resp to volparehealthscorecard
sc = VolparaHealthScorecard.parse_raw(resp)
print(sc)


client = instructor.patch(OpenAI())
sc = client.chat.completions.create(
    model="gpt-4-vision-preview",
    max_tokens=600,
    response_model=VolparaHealthScorecard,
    messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": f"Extract the metadata from the image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://i.ibb.co/DVfVmr2/volparahealth.png"
                    },
                },
            ],
        }]
    )
print(sc)