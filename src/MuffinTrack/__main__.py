from MuffinTrack import main,messageHandling

if __name__=="__main__":    
    try:        
        main()
    except Exception as e:
        MessageToSend = 'Unhandled error: {}'.format(e)
        messageHandling('Unhandled',MessageToSend)