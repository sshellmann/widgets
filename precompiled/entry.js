var $ = require("jquery");
require("bootstrap");
require("bootstrap/dist/css/bootstrap.css");
var React = require("react");
var ReactDOM = require("react-dom");
require("font-awesome-webpack");

const order = {
    "number": "fg94nas2a1",
    "products": [
        {"id": "1", "name": "", "description": "", "price": "10.00", "features": ["tiny"], "category": "prime", "quantity": 3},
        {"id": "2", "name": "", "description": "", "price": "20.00", "features": ["small", "yellow"], "category": "prime", "quantity": 2},
        {"id": "5", "name": "", "description": "", "price": "50.00", "features": ["huge", "red"], "category": "extreme", "quantity": 10},
    ]
}


class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            categories: props.categories,
            products: [],
            order: {}
        };
    }

    componentDidMount() {
        $.ajax({
            url: "/widget/",
            dataType: 'json',
            type: 'get',
            cache: false,
            success: function(data) {
                this.setState({"products": data.widgets});
            }.bind(this)
        });
    }

    render() {
        return (
            <div className="container">
                <Store categories={this.state.categories} products={this.state.products}/>
                <ShoppingCart order={this.state.order}/>
            </div>
        );
    }
}

class Store extends React.Component {
    render() {
        var sections = this.props.categories.map(function(category, idx) {
            return <StoreSection key={idx} category={category} products={this.props.products}/>;
        }.bind(this));
        return (
            <div className="panel panel-default">
                <div className="panel-heading">
                    <h3 className="panel-title">Store</h3>
                </div>
                <div className="panel-body">
                    {sections}
                </div>
            </div>
        );
    }
}

class StoreSection extends React.Component {
    render() {
        var productDisplays = this.props.products.map(function(product, idx) {
            if (product.category == this.props.category.name) {
                return <ProductDisplay key={idx} product={product}/>;
            }
        }.bind(this));
        return (
            <div>
                <h2><small>{this.props.category.label}</small></h2>
                <div className="row">
                    {productDisplays}
                </div>
            </div>
        );
    }
}

class ProductDisplay extends React.Component {
    render() {
        var features = this.props.product.features.map(function(feature, idx) {
            return <li key={idx}>{feature}</li>;
        });
        var quantity;
        if (this.props.product.quantity && this.props.product.quantity > 0) {
            quantity = <span>Only {this.props.product.quantity} left!</span>;
        } else if (quantity === 0) {
            quantity = <span>Sold Out!</span>;
        } else {
            quantity = null;
        }
        return (
            <div className="col-xs-6 col-sm-4 col-med-2 col-lg-2">
                <div className="thumbnail">
                    <div className="panel">
                        <div><h4>{this.props.product.name}</h4></div>
                        <p>{this.props.product.description}</p>
                        <div><ul style={{paddingLeft:"0px"}}><ul>{features}</ul></ul></div>
                        {quantity}
                        <div className="input-group">
                            <span className="input-group-addon">$</span>
                            <input type="text" style={{backgroundColor:"#fff"}} className="form-control" readOnly="readonly" value={this.props.product.price}/>
                        </div>
                    </div>
                    <div style={{textAlign:"center"}}>
                        <button type="button" className="btn btn-primary btn-xs" style={{width:"100%"}}>Add to Cart</button>
                    </div>
                </div>
            </div>
        );
    }
}

class ShoppingCart extends React.Component {
    getTotal(products) {
        if (products) {
            var total = products.reduce(function(product1, product2) {
                return (product1.price * product1.quantity) + (product2.price * product2.quantity);
            }, 0);
            return total;
        } else {
            return "0.00"
        }
    }

    render() {
        if (this.props.order.products) {
            var orders = this.props.order.products.map(function(product, idx) {
                return <OrderItem key={idx} product={product}/>;
            });
        } else {
            var orders = null;
        }
        return (
            <div className="panel panel-default">
                <div className="panel-heading">
                    <h3 className="panel-title">Shopping Cart</h3>
                </div>
                <div className="panel-body">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Description</th>
                                <th>Features</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {orders}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colSpan="3" style={{textAlign:'right'}}><strong>Total:</strong></td>
                                <td colSpan="3">{this.getTotal(this.props.order.products)}</td>
                            </tr>
                        </tfoot>
                    </table>
                    <button type="button" className="btn-block btn btn-primary">
                        <i className="fa fa-check"></i>
                        <span> Submit</span>
                    </button>
                </div>
            </div>
        );
    }
}

class OrderItem extends React.Component {
    render() {
        var product = this.props.product;
        var features = product.features.map(function(feature, idx) {
            return <li key={idx}>{feature}</li>;
        });
        return (
            <tr>
                <td>{product.name}</td>
                <td>{product.description}</td>
                <td><ul className="list-inline">{features}</ul></td>
                <td>{product.price}</td>
                <td>
                    <div className="form-group form-group-sm" style={{marginBottom:'0',width:'110px'}}>
                        <div className="">
                            <div className="input-group">
                                <span className="input-group-btn">
                                    <button type="button" className="btn btn-sm btn-default"><i className="fa fa-minus"></i></button>
                                </span>
                                <input style={{textAlign:'right'}} type="text" defaultValue={product.quantity} className="form-control"/>
                                <span className="input-group-btn">
                                    <button type="button" className="btn btn-sm btn-default"><i className="fa fa-plus"></i></button>
                                </span>
                            </div>
                        </div>
                    </div>
                </td>
                <td>
                    <button type="button" className="btn btn-sm btn-default">
                        <i className="fa fa-remove"></i>
                    </button>
                </td>
            </tr>
        );
    }
}
 
$(document).ready(function() {
    ReactDOM.render(
        <App categories={categories}/>,
        document.getElementById("app-container")
    );
});
