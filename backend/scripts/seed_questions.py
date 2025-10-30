from config.firebase_config import db
q = {
  "title":"Two Sum",
  "description":"Given array find two indices...",
  "difficulty":"Easy",
  "input_format":"array",
  "output_format":"indices",
  "sample_input":"[2,7,11,15], target=9",
  "sample_output":"[0,1]",
  "tags":["array","hashmap"]
}
db.collection("questions").document("Q101").set(q)
db.collection("questions").document("Q101").collection("languages").document("python").set({
  "template":"def two_sum(nums, target):\n    # write code\n    pass"
})
db.collection("test_cases").add({
  "questionId":"Q101",
  "input":"2 7 11 15\n9",
  "expectedOutput":"0 1",
  "visible": True
})
print("seeded")