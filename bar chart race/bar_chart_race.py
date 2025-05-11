# ---------------------
# Step 1: Import libraries
# ---------------------
import pandas as pd
import bar_chart_race as bcr
import matplotlib.pyplot as plt
from PIL import Image, ImageSequence
import os

# Load dataset and set encoding to 'latin1' to handle special characters
df = pd.read_csv('data/superstore.csv', encoding = 'latin1')

# Convert order date to datetime
df['Order Date'] = pd.to_datetime(df['Order Date'])

# Extract year from order date
df['Year'] = df['Order Date'].dt.year

# Group by year and sub-category to get total sales
yearly_sale = df.groupby(['Year', 'Sub-Category'])['Sales'].sum().reset_index()

# Pivot our dataset to have years as index and sub-categories as columns
df_pivot = yearly_sale.pivot(index='Year', columns='Sub-Category', values='Sales').fillna(0)

# Save the cleaned dataset to a CSV file
df_pivot.to_csv('data/superstore_cleaned.csv')


# ---------------------
# Step 2: Read the cleaned dataset and prepare for visualization
# ---------------------

# Read CSV file with yearly data, using 'Year' column as index
df_cleaned = pd.read_csv('data/superstore_cleaned.csv', index_col = 'Year')

# Convert all columns to numeric format to ensure proper handling of values
df_cleaned = df_cleaned.apply(pd.to_numeric)


# ---------------------
# Step 3: Create optimized charts for different platforms
# ---------------------

def bar_chart_race(output_file, figsize, period_label_pos, left_margin=0.25, right_margin=0.75):
    """Create a bar chart race with specified dimensions and layout"""
    # Create figure with proper margins and size
    fig, ax = plt.subplots(figsize=figsize, dpi=240)  # Use higher DPI for social media
    
    # Remove all borders
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Remove ticks and labels from x-axis
    ax.get_xaxis().set_visible(False)

    # Set chart title manually
    ax.set_title('Yearly Sales by Sub-Categories', fontsize=16, weight='bold', color='#333', pad=20)
    
    # Adjust margins to ensure all elements are visible and not cut off
    plt.subplots_adjust(left=left_margin, right=right_margin, bottom=0.05, top=0.9)
    
    # Create the bar chart race
    bcr.bar_chart_race(
        df=df_cleaned,                   # Our prepared DataFrame (years as index, categories as columns)
        filename=output_file,            # Temporary output file (will be modified later)
        fig=fig,                         # Use our pre-configured figure with proper margins
        orientation='h',                 # Horizontal bars are better for reading category names
        sort='desc',                     # Sort bars by value in descending order
        fixed_order=False,               # Allow bars to reorder each frame based on values
        fixed_max=True,                  # Keep a consistent scale throughout animation
        steps_per_period=60,             # Higher values create smoother animations (but larger files)
        interpolate_period=False,        # Don't interpolate between years (use actual data points)
        label_bars=True,                 # Show values on the bars
        bar_size=0.9,                    # Bar thickness (0-1), allows for spacing between bars
        period_label={                   # Configuration for the year label
            'x': period_label_pos[0],    # Horizontal position (0-1, where 1 is right edge). Don't directly position the year label by themselves. They're simply placeholders that receive the actual position values when we call the function for each version of the chart.
            'y': period_label_pos[1],    # Vertical position (0-1, where 1 is top edge). Don't directly position the year label by themselves. They're simply placeholders that receive the actual position values when we call the function for each version of the chart.
            'ha': 'right',               # Horizontal alignment of text
            'va': 'bottom',              # Vertical alignment of text
            'size': 20,                  # Font size
            'weight': 'bold',            # Font weight
            'color': '#333'              # Font color (grey)
        },
        period_fmt='Year: {x: .0f}',     # Format of the year label
        period_length=600,               # Duration of each period in milliseconds
        figsize=figsize,                 # Figure size again (matches our initial figure)
        dpi=240,                         # Higher DPI for better quality on social media
        cmap='dark12',                   # Color palette with distinct colors
        title='Yearly Sales by Sub-Categories',   # Chart title
        bar_label_size=11,               # Size of the value labels on bars
        tick_label_size=10,              # Size of category labels on y-axis
        scale='linear',                  # Use linear scale for values
        writer='pillow',                 # GIF writer to use (pillow works on most systems)
        bar_kwargs={'alpha': 0.8},       # Slight transparency for bars
        filter_column_colors=True        # Keep consistent colors for categories
    )
    
    # Add a 2-second pause at the end of the GIF to ensures viewers can see the final state
    with Image.open(output_file) as im:
        # Extract all frames from the original GIF
        frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
        # Save as a new GIF with modified frame durations
        frames[0].save(
            f"final_{output_file}",                                         # New filename with 'final_' prefix
            save_all=True,                                                  # Save all frames
            append_images=frames[1:],                                       # Add all frames after the first
            duration=[im.info['duration']] * (len(frames) - 1) + [2000],    # Last frame shows for 2 seconds
            loop=0                                                          # Loop forever (0 = infinite)
        )
    
    # Remove the temporary file created by bar_chart_race
    # We only need the final version with the pause
    os.remove(output_file)

    # Close the figure to free up memory and prevent hanging
    plt.close(fig)

    # Check if the output file was created successfully
    print(f"Created {output_file} with dimensions {figsize}")

# Set matplotlib to non-interactive mode to prevent blocking the script
plt.ioff()

# Create LinkedIn optimized version (landscape format)
# LinkedIn works best with wider images in landscape orientation
bar_chart_race(
    'bar_chart_race_linkedin.gif',    # Output filename 
    figsize = (10, 6),              # Landscape format (width > height)
    period_label_pos = (0.98, 0.02) # Position of year label
)

# Create Instagram feed optimized version (square format)
# Instagram feed posts display best as squares
bar_chart_race(
    'bar_chart_race_instagram_feed.gif',    # Output filename
    figsize = (8, 8),                   # Perfect square dimensions
    period_label_pos = (0.98, 0.02),    # Position of year label
    right_margin = 0.78                 # Slightly more right margin for square format
)

# Create Instagram Stories optimized version (portrait format)
# Instagram Stories use 9:16 aspect ratio (portrait orientation)
bar_chart_race(
    'bar_chart_race_instagram_story.gif', # Output filename
    figsize = (8, 10),                  # Portrait format (height > width)
    period_label_pos = (0.98, 0.02),    # Position of year label
    right_margin = 0.78                 # Slightly more right margin for better visibility
)

# Close all figures to free up memory and print success message
plt.close('all') 
print("Charts created successfully!")