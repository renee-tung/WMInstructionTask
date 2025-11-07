"""
Lookup table to determine instruction prompt used in each trial.
"""

def get_instruction_text(category, trial_axis_name, anti_task, prompt_variant, equivalent_variant_id):
    """
    Get instruction text based on trial parameters.
    
    Parameters:
    -----------
    category : int
        Category index (0=Animals, 1=Cars, 2=Faces, 3=Fruits)
    trial_axis_name : str
        Name of the axis ('New', 'Identical', 'Count', 'Colorful')
    anti_task : bool or int
        Whether this is an anti-task trial
    prompt_variant : bool or int
        Which prompt variant to use
    equivalent_variant_id : bool or int
        Which equivalent variant ID to use
    
    Returns:
    --------
    text : str
        Instruction text for the trial
    """
    # Convert to boolean for easier handling
    anti_task = bool(anti_task)
    prompt_variant = bool(prompt_variant)
    equivalent_variant_id = bool(equivalent_variant_id)
    
    # Singular category names
    singular_category_labels = ['animal', 'car', 'face', 'item']
    plural_category_labels = ['animals', 'cars', 'faces', 'items']
    alternative_singular_category_labels = ['creature', 'vehicle', 'person', 'object']
    alternative_plural_category_labels = ['creatures', 'vehicles', 'people', 'objects']
    
    # Category is already 0-indexed
    cat_idx = category
    
    if trial_axis_name == 'New':
        if anti_task:
            if prompt_variant:
                if category == 2:
                    if equivalent_variant_id:
                        text = f'Avoid the younger {singular_category_labels[cat_idx]}'
                    else:
                        text = f'Do not select the youthful {alternative_singular_category_labels[cat_idx]}'
                else:
                    if equivalent_variant_id:
                        text = f'Avoid the newer {singular_category_labels[cat_idx]}'
                    else:
                        text = f'Do not select the more modern {alternative_singular_category_labels[cat_idx]}'
            else:
                if category == 2:
                    if equivalent_variant_id:
                        text = f'Avoid the older {singular_category_labels[cat_idx]}'
                    else:
                        text = f'Do not select the more aged {alternative_singular_category_labels[cat_idx]}'
                else:
                    if equivalent_variant_id:
                        text = f'Avoid the older {singular_category_labels[cat_idx]}'
                    else:
                        text = f'Do not select the less modern {alternative_singular_category_labels[cat_idx]}'
        else:
            if prompt_variant:
                if category == 2:
                    if equivalent_variant_id:
                        text = f'Choose the younger {singular_category_labels[cat_idx]}'
                    else:
                        text = f'Select the more youthful {alternative_singular_category_labels[cat_idx]}'
                else:
                    if equivalent_variant_id:
                        text = f'Choose the newer {singular_category_labels[cat_idx]}'
                    else:
                        text = f'Select the more modern {alternative_singular_category_labels[cat_idx]}'
            else:
                if category == 2:
                    if equivalent_variant_id:
                        text = f'Choose the older {singular_category_labels[cat_idx]}'
                    else:
                        text = f'Select the more aged {alternative_singular_category_labels[cat_idx]}'
                else:
                    if equivalent_variant_id:
                        text = f'Choose the older {singular_category_labels[cat_idx]}'
                    else:
                        text = f'Select the less modern {alternative_singular_category_labels[cat_idx]}'
    
    elif trial_axis_name == 'Identical':
        if anti_task:
            if prompt_variant:
                if equivalent_variant_id:
                    text = f'Are these {plural_category_labels[cat_idx]} different?'
                else:
                    text = f'Do these {alternative_plural_category_labels[cat_idx]} have different identities?'
            else:
                if equivalent_variant_id:
                    text = f'Are these different {plural_category_labels[cat_idx]}?'
                else:
                    text = f'Are these photos of different {alternative_plural_category_labels[cat_idx]}?'
        else:
            if prompt_variant:
                if equivalent_variant_id:
                    text = f'Are these {plural_category_labels[cat_idx]} the same?'
                else:
                    text = f'Are these photos of the same {alternative_singular_category_labels[cat_idx]}?'
            else:
                if equivalent_variant_id:
                    text = f'Are these {plural_category_labels[cat_idx]} identical?'
                else:
                    text = f'Do these {alternative_plural_category_labels[cat_idx]} have the same identity?'
    
    elif trial_axis_name == 'Count':
        if anti_task:
            if prompt_variant:
                if equivalent_variant_id:
                    text = f'Avoid the image with more {plural_category_labels[cat_idx]}'
                else:
                    text = f'Do not select the image with more {alternative_plural_category_labels[cat_idx]}'
            else:
                if equivalent_variant_id:
                    text = f'Avoid the image with fewer {plural_category_labels[cat_idx]}'
                else:
                    text = f'Do not select the image with fewer {alternative_plural_category_labels[cat_idx]}'
        else:
            if prompt_variant:
                if equivalent_variant_id:
                    text = f'Choose the image with more {plural_category_labels[cat_idx]}'
                else:
                    text = f'Select the image with more {alternative_plural_category_labels[cat_idx]}'
            else:
                if equivalent_variant_id:
                    text = f'Choose the image with fewer {plural_category_labels[cat_idx]}'
                else:
                    text = f'Select the image with fewer {alternative_plural_category_labels[cat_idx]}'
    
    elif trial_axis_name == 'Colorful':
        if anti_task:
            if prompt_variant:
                if equivalent_variant_id:
                    text = f'Avoid the more colorful {singular_category_labels[cat_idx]}'
                else:
                    text = f'Do not select the {alternative_singular_category_labels[cat_idx]} with more colors'
            else:
                if equivalent_variant_id:
                    text = f'Avoid the less colorful {singular_category_labels[cat_idx]}'
                else:
                    text = f'Do not select the {alternative_singular_category_labels[cat_idx]} with fewer colors'
        else:
            if prompt_variant:
                if equivalent_variant_id:
                    text = f'Choose the more colorful {singular_category_labels[cat_idx]}'
                else:
                    text = f'Select the {alternative_singular_category_labels[cat_idx]} with more colors'
            else:
                if equivalent_variant_id:
                    text = f'Choose the less colorful {singular_category_labels[cat_idx]}'
                else:
                    text = f'Select the {alternative_singular_category_labels[cat_idx]} with fewer colors'
    
    else:
        text = ''
    
    return text

