from filters import filter1, filter2, filter3
import time


def main():
    total_start_time = time.time()

    # Run filter1
    print("Running filter1...")
    start_time = time.time()
    filter1.fetch_issuers()
    end_time = time.time()
    print(f"filter1 completed in {end_time - start_time:.2f} seconds.\n")

    # Run filter2
    print("Running filter2...")
    start_time = time.time()
    filter2.main()
    end_time = time.time()
    print(f"filter2 completed in {end_time - start_time:.2f} seconds.\n")

    # Run filter3
    print("Running filter3...")
    start_time = time.time()
    filter3.main()
    end_time = time.time()
    print(f"filter3 completed in {end_time - start_time:.2f} seconds.\n")

    total_end_time = time.time()
    print(f"Pipeline completed in {total_end_time - total_start_time:.2f} seconds.")


if __name__ == "__main__":
    main()
