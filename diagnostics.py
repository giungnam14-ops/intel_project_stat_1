import sys

with open('diag_log.txt', 'w', encoding='utf-8') as f:
    def log(msg):
        print(msg)
        f.write(str(msg) + '\n')
        f.flush()

    try:
        log("Checking imports...")
        from preprocessing import load_and_preprocess_data
        from modeling import train_and_evaluate
        log("Imports OK.")
        
        log("Loading data...")
        X, y, le, df_processed = load_and_preprocess_data('data.xlsx')
        log("Data OK.")
        
        log("Training model...")
        lr_model, rf_model, metrics, split_data, cv_scores = train_and_evaluate(X, y)
        log("Model OK.")
        
        log("Everything is working correctly.")
    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        f.write(traceback.format_exc())
