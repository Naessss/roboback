from inference_sdk import InferenceHTTPClient
import os

robo_api_key = os.getenv("ROBOFLOW_API_KEY")

def detect_cardamage(image):
  client = InferenceHTTPClient(
      api_url="https://detect.roboflow.com",
      api_key=robo_api_key
  )

  result = client.run_workflow(
      workspace_name="cardamage-5kvgs",
      workflow_id="detect-and-classify",
      images={
          "image": image
      },
      use_cache=True # cache workflow definition for 15 minutes
  )

  return result
