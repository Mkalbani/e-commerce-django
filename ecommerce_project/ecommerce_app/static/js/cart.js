function addToCart(product_id) {
    // Make an AJAX request to the add_to_cart view function
    $.ajax({
        url: '/add_to_cart/',
        type: 'POST',
        data: {
            product_id: product_id,
        },
        success: function(response) {
            // Product successfully added to cart
            alert('Product added to cart!');
        },
        error: function(error) {
            // An error occurred while adding the product to cart
            alert('An error occurred while adding the product to cart.');
        }
    });
}
