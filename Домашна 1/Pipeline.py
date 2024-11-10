from filters import filter1, filter2, filter3
import time

def main():
    # Record the start time of the entire script
    total_start_time = time.time()

    # Run filter1
    print("Running filter1...")
    start_time = time.time()
    filter1.fetch_issuers()  # Assuming filter1.py has a main function
    end_time = time.time()
    print(f"filter1 completed in {end_time - start_time:.2f} seconds.\n")

    # Run filter2
    print("Running filter2...")
    start_time = time.time()
    filter2.main()  # Assuming filter2.py has a main function
    end_time = time.time()
    print(f"filter2 completed in {end_time - start_time:.2f} seconds.\n")

    # Run filter3
    print("Running filter3...")
    start_time = time.time()
    filter3.main()  # Assuming filter3.py has a main function
    end_time = time.time()
    print(f"filter3 completed in {end_time - start_time:.2f} seconds.\n")

    # Record the end time of the entire script and calculate the total time
    total_end_time = time.time()
    print(f"Pipeline completed in {total_end_time - total_start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
