from openai import OpenAI
import instructor

from typing import Optional
from pydantic import BaseModel, AfterValidator, BeforeValidator, ValidationError, Field, model_validator
from typing_extensions import Annotated

# Usecase 0: You want to generate a data structure using an LLM.
# Let the llm populate  the data structure for you.
client = instructor.patch(OpenAI())
def valid_name(name: str) -> bool:
    if not name[0].isupper():
        raise ValueError(f"Name must start with a capital letter: {name}")
    return name

class UserDetail(BaseModel):
    name: Annotated[str, AfterValidator(valid_name)]
    age: int

user = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=UserDetail,
    messages=[
        {"role": "user", "content": "Extract jason is 25 years old"},
    ]
)
print(user)
assert isinstance(user, UserDetail)
assert user.name == "Jason"
assert user.age == 25

print(user)


# Usecase 1: You want to validate a data-structure using an LLM
# In this case, you are a leafs-fan and only accept answers that are positive
# about the leafs.
# Validations can be:
#   - verify text is valid (expected answer, tone, punctuation, etc.
#   - TODO: Add vision capability?
class QuestionAnswer(BaseModel):
    question: str
    answer: Annotated[str, BeforeValidator(instructor.llm_validator("Answer like you are a Toronto Maple Leafs fan. Don't care about grammar/vocab/punctuation"))]

try:
    qa = QuestionAnswer(question="What is your favorite thing about Canada?", answer="The Toronto Maple Leafs.")
except ValidationError as e:
    print(e)


# Usecase 2: If the LLM cannot populate your data-structure, give it a mechanism
# to communicate this back to you. Wrap your model in another model that gives
# the LLM an escape hatch
class Country(BaseModel):
    name: str
    population: int
    capital: str

class MaybeCountry(BaseModel):
    result: Optional[Country] = Field(default=None)
    error: Optional[bool] = Field(default=False)
    error_description: Optional[str] = Field(default="")

    def __bool__(self):
        return not self.error

    @classmethod
    def populate(cls, description: str) -> "MaybeCountry":
       return client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_model=cls,
        messages=[
            {"role": "user", "content": f"Only respond with real countries that exist in 2023\n {description}"}
        ]
    )

c = MaybeCountry.populate("Give me a country that has over 100 million people and is in Asia")
print(c)

# GPT3-5 gave a passing answer, but it was not a real country
# GPT-4-turbo did the right thing
c = MaybeCountry.populate("A country that has over 1 billion people and is in Europe")
print(c)
c = MaybeCountry.populate("The country of Abstenforth")
print(c)
c = MaybeCountry.populate("Unknown country")
print(c)


# Usecase 3: Add the chain-of-thought field to figure out how the LLM got to its
# answer
class MaybeCountryCOT(MaybeCountry):
    chain_of_thought: str = Field(default="Describe your step by step reasoning on how you got to your answer")

c = MaybeCountryCOT.populate("A country that has over 1 billion people and is in Europe")
print(c)


# Usecase 4: I want to map one set of requirements to another.
# There are many detector ais that compute areas of interest on a medical image. Each outputs a file containing areas
# of interest and a score, usually a probability.
# I want to provide two sets of requirement: high-level product and low-level software ones.
class Requirement(BaseModel):
    id: str
    description: str


class Requirements(BaseModel):
    requirements: list[Requirement]

class Trace(BaseModel):
    chain_of_thought: str = Field(default="Step by step reasoning on how the source requirement matches the target requirement")
    source: Requirement
    target: Requirement

product_requirements = Requirements(
    requirements=[
        Requirement(id="P1", description="The system shall generate a JSON file containg areas of interest on a medical image"),
        Requirement(id="P2", description="The system shall generate a json file contain findings composed of a bounding box and a probability/score"),
        Requirement(id="P3", description="The system shall generate this json file for all exams it processed."),
        Requirement(id="P4", description="The system shall send this json file to Amazon S3")
    ]
)

software_requirements = Requirements(
    requirements=[
        Requirement(id="S1", description="The system shall generate a JSON file encapsulating all findings on a medical image"),
        Requirement(id="S2", description="The system shall send the file to a configured AWS S3 Bucket"),
        Requirement(id="S3", description="The system shall output a bounding box composed of 4 coordinates for each finding"),
        Requirement(id="S4", description="The system shall output a score for each finding in the range [0,100]"),
        Requirement(id="S5", description="The system shall output a maximum of 8 findings per image in the JSON file"),
        Requirement(id="S6", description="The system shall output a minimum of 0 findings per image in the JSON file"),
        Requirement(id="S7", description="The system shall output a JSON filefor exams that do not satisfy our input criteria"),
        Requirement(id="S8", description="The system shall output a JSON file for exams that do satisfy our input criteria")
    ]
)


class Traces(BaseModel):
    chain_of_thought: str = Field(default="Step by step reasoning on how the source requirement matches the target requirement in traces")
    product_requirements: Requirements
    software_requirements: Requirements
    traces: list[Trace]

    @classmethod
    def populate(cls, query):
       return client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_model=cls,
        max_retries=2,
        messages=[
            {"role": "user", "content": query}
        ]
    )

    @model_validator(mode="after")
    def validate_traces(self) -> "Traces":
        for trace in self.traces:
            if trace.source not in product_requirements.requirements:
                raise ValueError(f"Source requirement {trace.source} is not in the product requirements")
            if trace.target not in software_requirements.requirements:
                raise ValueError(f"Target requirement {trace.target} is not in the software requirements")
        return self

# Convert the product_requirements to json
product_requirements_json = product_requirements.model_dump_json()
software_requirements_json = software_requirements.model_dump_json()

traces = Traces.populate(f"Map the following product requirements to software requirements. Also return the product_requirements and software_requirements too. Please populate a unique reason in the chain-of_thought field for each mapping. :\nProduct Requirements:{product_requirements_json}\n Software Requirements{software_requirements_json}")
print(traces)
# save traces to a json file
with open("traces.json", "w") as f:
    f.write(traces.model_dump_json())

# Generate a csv mapping the product_iq to softwar_id from traces
import pandas as pd
df = pd.DataFrame.from_records([{"product_id": trace.source.id, "software_id": trace.target.id} for trace in traces.traces])
print(df)
df.to_csv("product_to_software.csv", index=False)

