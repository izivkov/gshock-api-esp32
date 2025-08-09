from lib import display

def main():
    # Example key-value data
    data = [
        ('Temp', '25°C'),
        ('Pressure', '1013hPa'),
        ('Humidity', '60%'),
        ('Home Town', 'Toronto'),
        ('Last Update', '18:31')
    ]

    # Initialize and display the data.
    display.display_data(data)
    print("Data displayed successfully!!!")
    
if __name__ == "__main__":
    main()
