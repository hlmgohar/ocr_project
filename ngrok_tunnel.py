from pyngrok import ngrok
public_url = ngrok.connect(8000)
ngrok.set_auth_token("2o9Uubn5TwlWBFRp0IKl7FYHvbF_3XmsvLMwe1bX3GnV2RChp")
print(f"Public URL: {public_url}")
