// 1. Carichiamo l'ambiente PrestaShop
require_once(dirname(__FILE__).'/config/config.inc.php');
require_once(dirname(__FILE__).'/init.php');

// 2. Recuperiamo i parametri dall'URL
$id_cart = (int)Tools::getValue('id_cart');
$token = Tools::getValue('token'); // La secure_key del carrello

// 3. Carichiamo l'oggetto carrello dal database
$cart = new Cart($id_cart);

// 4. Verifica di sicurezza
// Controlliamo che il carrello esista e che il token sia corretto
if (Validate::isLoadedObject($cart) && $cart->secure_key == $token) {
    
    // Associao il carrello alla sessione del browser (Cookie)
    $context = Context::getContext();
    $context->cookie->id_cart = (int)$cart->id;
    $context->cart = $cart;
    
    // Aggiorniamo il carrello per assicurarci che sia legato al cliente corrente se loggato
    $context->cart->id_customer = (int)$context->customer->id;
    $context->cart->update();

    // 5. Reindirizziamo l'utente alla pagina dell'ordine
    Tools::redirect('index.php?controller=order');
} else {
    // Se qualcosa non va, rimandiamo alla Home con un errore
    die("Errore: Carrello non valido o sessione scaduta.");
} 
