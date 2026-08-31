Hola! This project is a RAG pipe line. Wanted to show that small AI models when flooded with information can do better than just alone. As part of a camp made this.
This project uses various things like Anythingllm, yolov8 for image cuttings, clip this was an amazing model i found clip.py is the backbone to classify image with a food name very good accuracy. 
One of the cool feature is we use sophisticated line where we ask AI only to pick a food item form initially classified list so accuracy can be so good. 
I felt it is very scalable in horizontal directions without much burden on firm servers. Learnt about streaming, tokens and what not many more download and test this new idea.

| #     | Model                        | Algorithm / Technology               | Purpose                                                                     |
| ----- | ---------------------------- | ------------------------------------ | --------------------------------------------------------------------------- |
| **1** | **Health Intent Classifier** | **TF-IDF + Logistic Regression**     | Determines whether the user's query is health-related or non-health-related |
| **2** | **Disease Predictor**        | **TF-IDF + Multinomial Naive Bayes** | Predicts possible diseases from the user's symptom text                     |
| **3** | **Food Image Classifier**    | **CLIP**                             | Identifies food from an uploaded image                                      |

