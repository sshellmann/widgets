var $ = require("jquery");
require("bootstrap");
var React = require("react");
var ReactDOM = require("react-dom");
require("bootstrap/dist/css/bootstrap.css");
require("font-awesome-webpack");

const products = {
    "1" : {"name": "", "description": "", "price": "10.00", "features": ["small", "red"], "category": "prime"},
    "2" : {"name": "", "description": "", "price": "20.00", "features": ["small", "blue"], "category": "prime"},
    "3" : {"name": "", "description": "", "price": "30.00", "features": ["big", "red"], "category": "elite"},
    "4" : {"name": "", "description": "", "price": "40.00", "features": ["big", "blue"], "category": "elite"},
    "5" : {"name": "", "description": "", "price": "50.00", "features": ["huge", "red"], "category": "extreme"},
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            products: products
        };
    }

    render() {
        return (
            <div className="container">
                <ShoppingCart products={products}/>
            </div>
        );
    }
}

class ShoppingCart extends React.Component {
    submit() {
        const selection = this.refs.cart.getSelection()
        alert(JSON.stringify(selection))
    }

    addItem(key) {
        this.refs.cart.addItem(key, 1, this.props.products[key])
    }

    render() {
        const products = this.props.products
        return (
            <div className="panel panel-default">
                <div className="panel-body">
                    <table className="table cart">
                        <thead>
                            <tr>
                                <th>Artist</th>
                                <th>Title</th>
                                <th>Format</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Alborosie</td>
                                <td>2 Times Revolution</td>
                                <td>LP</td>
                                <td>11.48</td>
                                <td>
                                    <div className="form-group form-group-sm" style={{marginBottom:'0',width:'110px'}}>
                                        <div className="">
                                            <div className="input-group">
                                                <span className="input-group-btn">
                                                    <button type="button" className="btn btn-sm btn-default"><i className="fa fa-minus"></i></button>
                                                </span>
                                                <input style={{textAlign:'right'}} type="text" defaultValue="1" className="form-control"/>
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
                            <tr>
                                <td>Alborosie</td>
                                <td>Escape from Babylon</td>
                                <td>LP</td>
                                <td>11.76</td>
                                <td>
                                    <div className="form-group form-group-sm" style={{marginBottom:'0',width:'110px'}}>
                                        <div className="">
                                            <div className="input-group">
                                                <span className="input-group-btn">
                                                    <button type="button" className="btn btn-sm btn-default"><i className="fa fa-minus"></i></button>
                                                </span>
                                                <input style={{textAlign:'right'}} type="text" defaultValue="1" className="form-control"/>
                                                <span className="input-group-btn"><button type="button" className="btn btn-sm btn-default"><i className="fa fa-plus"></i></button></span>
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <button type="button" className="btn btn-sm btn-default"><i className="fa fa-remove"></i></button>
                                </td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colSpan="3" style={{textAlign:'right'}}><strong>Total:</strong></td>
                                <td colSpan="3">23.24</td>
                            </tr>
                        </tfoot>
                    </table>
                    <button type="button" className="btn-block btn btn-primary">
                        <i className="fa fa-check"></i>
                        <span> Submit</span>
                    </button>
                </div>
            </div>
        )
    }
}
 
$(document).ready(function() {
    ReactDOM.render(
        <App products={products} />,
        document.getElementById("app-container")
    );
});
