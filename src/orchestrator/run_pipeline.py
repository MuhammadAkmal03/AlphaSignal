from ais.ais_stream import collect_daily_ais_data
from uso.uso_fetcher import fetch_uso_data
from eia.eia_fetcher import fetch_eia_data
from nlp.nlp_demand_score import generate_demand_score
# from sentinel.sentinel_refinery_fetcher import download_sentinel_images

def run_pipeline():
    print("\n====== AlphaSignal Pipeline START ======\n")

    fetch_uso_data()
    fetch_eia_data()
    collect_daily_ais_data()
    generate_demand_score()
    # download_sentinel_images()  

    print("\n====== Pipeline COMPLETE ======\n")

if __name__ == "__main__":
    run_pipeline()
