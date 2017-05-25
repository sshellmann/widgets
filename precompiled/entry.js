var $ = require("jquery");
require("bootstrap");
require("bootstrap/dist/css/bootstrap.css");
var React = require("react");
var ReactDOM = require("react-dom");
require("font-awesome-webpack");
var update = require('react-addons-update');
var _ = require('lodash');

const order = {
    "number": "fg94nas2a1",
    "items": [
        {"id": "1", "name": "", "description": "", "price": "10.00", "features": ["tiny"], "category": "prime", "quantity": 3},
        {"id": "2", "name": "", "description": "", "price": "20.00", "features": ["small", "yellow"], "category": "prime", "quantity": 2},
        {"id": "5", "name": "", "description": "", "price": "50.00", "features": ["huge", "red"], "category": "extreme", "quantity": 10},
    ]
}

/*
 * Widgets
[{id: 5, category: "elite", price: "10.00", features: ["Small", "Chrome"], name: "Widget3",…},…]
{id: 5, category: "elite", price: "10.00", features: ["Small", "Chrome"], name: "Widget3",…}
{id: 6, category: "elite", price: "10.00", features: ["Large", "Chrome"], name: "Widget4",…}
{id: 7, category: "extreme", price: "15.00", features: ["Huge", "Red"], name: "Widget5",…}
{id: 8, category: "extreme", price: "15.00", features: ["Huge", "Blue"], name: "Widget6",…}
{id: 3, category: "prime", price: "5.00", features: ["Small", "Red"], name: "Widget1",…}
{id: 4, category: "prime", price: "5.00", features: ["Small", "Blue"], name: "Widget2",…}
*/


class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            categories: props.categories,
            products: [],
            order: {}
        };
        this.addWidgetToCart = this.addWidgetToCart.bind(this);
        this.decrementItem = this.decrementItem.bind(this);
        this.incrementItem = this.incrementItem.bind(this);
        this.removeItem = this.removeItem.bind(this);
        this.loadOrder = this.loadOrder.bind(this);
    }

    componentDidMount() {
        $.ajax({
            url: "/widget/",
            dataType: 'json',
            type: 'get',
            cache: false,
            success: function(data) {
                this.setState({"products": data});
            }.bind(this)
        });
    }

    newOrder(widget) {
        $.ajax({
            url: "/order/",
            dataType: 'json',
            type: 'post',
            cache: false,
            data: {
                "widget": widget.id,
                "quantity": 1,
            },
            success: function(data) {
                this.setState({"order": data});
            }.bind(this)
        });
    }

    findIndex(item) {
        var idx = null;
        this.state.order.items.map(function(item_, idx_) {
            if (item.id === item_.id) {
                idx = idx_;
            }
        });
        return idx;
    }

    updateQuantity(item, newQuantity) {
        $.ajax({
            url: "/order/item/" + item.id,
            dataType: 'json',
            type: 'put',
            cache: false,
            data: {
                "order": this.state.order.id,
                "widget": item.widget.id,
                "quantity": newQuantity,
            },
            success: function(data) {
                var itemIdx = this.findIndex(item);
                var orderClone = _.extend({}, this.state.order);
                orderClone.items[itemIdx] = data;
                this.setState({"order": orderClone});
            }.bind(this)
        });
    }

    newItem(widget) {
        $.ajax({
            url: "/order/item/",
            dataType: 'json',
            type: 'post',
            cache: false,
            data: {
                "order": this.state.order.id,
                "widget": widget.id,
                "quantity": 1,
            },
            success: function(data) {
                this.setState({
                    order: update(this.state.order, {items: {$push: [data]}})
                })
            }.bind(this)
        });
    }

    addWidgetToCart(widget) {
        if ($.isEmptyObject(this.state.order)) {
            this.newOrder(widget);
        } else {
            var existing = null;
            this.state.order.items.map(function(item) {
                if (item.widget.id == widget.id) {
                    existing = item;
                }
            });
            if (existing !== null) {
                this.updateQuantity(existing, existing.quantity + 1);
            } else {
                this.newItem(widget);
            }
        }
    }

    removeItem(item) {
        $.ajax({
            url: "/order/item/" + item.id,
            type: 'delete',
            cache: false,
            success: function() {
                var idx = this.findIndex(item);
                if (idx !== null) {
                    if (this.state.order.items.length > 1) {
                        this.setState({
                            order: update(this.state.order, {items: {$splice: [[idx, 1]]}})
                        })
                    } else {
                        this.setState({order: {}});
                    }
                }
            }.bind(this)
        });
    }

    incrementItem(item) {
        this.updateQuantity(item, item.quantity + 1);
    }

    decrementItem(item) {
        var newQuantity = item.quantity - 1;
        if (newQuantity <= 0) {
            this.removeItem(item);
        } else {
            this.updateQuantity(item, item.quantity - 1);
        }
    }

    loadOrder(orderNumber, callback) {
        $.ajax({
            url: "/order/" + orderNumber,
            dataType: 'json',
            type: 'get',
            cache: false,
            success: function(data) {
                this.setState({"order": data});
                callback();
            }.bind(this)
        });
    }

    render() {
        return (
            <div className="container">
                <Store categories={this.state.categories} products={this.state.products} addWidgetToCart={this.addWidgetToCart}/>
                <ShoppingCart order={this.state.order} decrementItem={this.decrementItem} incrementItem={this.incrementItem}
                    removeItem={this.removeItem} loadOrder={this.loadOrder}/>
            </div>
        );
    }
}

class Store extends React.Component {
    render() {
        var sections = this.props.categories.map(function(category, idx) {
            return <StoreSection key={idx} category={category} products={this.props.products} addWidgetToCart={this.props.addWidgetToCart}/>;
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
                return <ProductDisplay key={idx} product={product} addWidgetToCart={this.props.addWidgetToCart}/>;
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
    handleClickAddToCart() {
        this.props.addWidgetToCart(this.props.product);
    }

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
                        <button type="button" onClick={this.handleClickAddToCart.bind(this)} className="btn btn-primary btn-xs" style={{width:"100%"}}>Add to Cart</button>
                    </div>
                </div>
            </div>
        );
    }
}

class ShoppingCart extends React.Component {
    getTotal(items) {
        if (items) {
            var total = 0;
            items.map(function(item) {
                total += (item.widget.price * item.quantity);
            });
            return total.toFixed(2);
        } else {
            return "0.00"
        }
    }

    render() {
        if (this.props.order.items) {
            var orders = this.props.order.items.map(function(item, idx) {
                return <OrderItem key={idx} item={item} decrementItem={this.props.decrementItem}
                    incrementItem={this.props.incrementItem} removeItem={this.props.removeItem}/>;
            }.bind(this));
        } else {
            var orders = null;
        }
        var total = this.getTotal(this.props.order.items);

        if (! $.isEmptyObject(this.props.order)) {
            var orderInfo = <span> - {this.props.order.number}</span>;
        }
        return (
            <div className="panel panel-default">
                <div className="panel-heading">
                    <LoadOrder loadOrder={this.props.loadOrder}/>
                    <h3 className="panel-title">Shopping Cart{orderInfo}</h3>
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
                                <td colSpan="3">{total}</td>
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

class LoadOrder extends React.Component {
    handleSubmitLoad(evt) {
        evt.preventDefault()
        this.props.loadOrder(this.input.value, function() {this.input.value = ""}.bind(this));
    }

    render() {
        return (
            <form className="pull-right" onSubmit={evt => this.handleSubmitLoad.bind(this)(evt)}>
                <span>Load Order: </span>
                <input type="text" ref={(input) => this.input = input}/>
                <button type="submit" className="btn btn-xs btn-primary">
                    <span>Load</span>
                </button>
            </form>
        );
    }
}

class OrderItem extends React.Component {
    handleClickDecrement() {
        this.props.decrementItem(this.props.item);
    }

    handleClickIncrement() {
        this.props.incrementItem(this.props.item);
    }

    handleClickRemove() {
        this.props.removeItem(this.props.item);
    }

    render() {
        var item = this.props.item;
        if (item.quantity <= 0) {
            return null;
        }
        var features = item.widget.features.map(function(feature, idx) {
            return <li key={idx}>{feature}</li>;
        });
        return (
            <tr>
                <td>{item.widget.name}</td>
                <td>{item.widget.description}</td>
                <td><ul className="list-inline">{features}</ul></td>
                <td>{item.price}</td>
                <td>
                    <div className="form-group form-group-sm" style={{marginBottom:'0',width:'110px'}}>
                        <div className="">
                            <div className="input-group">
                                <span className="input-group-btn">
                                    <button type="button" onClick={this.handleClickDecrement.bind(this)} className="btn btn-sm btn-default"><i className="fa fa-minus"></i></button>
                                </span>
                                <input style={{textAlign:'right'}} readOnly="readonly" type="text" value={item.quantity} className="form-control"/>
                                <span className="input-group-btn">
                                    <button type="button" onClick={this.handleClickIncrement.bind(this)} className="btn btn-sm btn-default"><i className="fa fa-plus"></i></button>
                                </span>
                            </div>
                        </div>
                    </div>
                </td>
                <td>
                    <button type="button" onClick={this.handleClickRemove.bind(this)} className="btn btn-sm btn-default">
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
