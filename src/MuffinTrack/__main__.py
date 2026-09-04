from .MuffinTrack import cli,messageHandling

if __name__=="__main__":    
    try:        
         cli()
    except Exception as e:
        MessageToSend = 'Unhandled error: {}'.format(e)
        messageHandling('Unhandled',MessageToSend)