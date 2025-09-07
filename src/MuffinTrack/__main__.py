from MuffinTrack import main,errorHandling

if __name__=="__main__":    
    try:        
        main()
    except Exception as e:
        MessageToSend = 'Unhandled error: {}'.format(e)
        errorHandling('Unhandled',MessageToSend)