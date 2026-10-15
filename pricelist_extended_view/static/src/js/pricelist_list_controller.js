/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";

export class PricelistItemListController extends ListController {
    /**
     * Override the native action of the "New" button to open a modal for creating a new pricelist item.
     */
    async createRecord() {
        const activeId = this.props.context.active_id || this.props.context.default_pricelist_id;

        await this.actionService.doAction({
            name: "Create: Pricelist Rule",
            type: "ir.actions.act_window",
            res_model: "product.pricelist.item",
            views: [[false, "form"]],
            target: "new", // <-- Open the form in a modal
            context: {
                ...this.props.context,
                default_pricelist_id: activeId,
            },
        }, {
            onClose: () => this.model.load(),
        });
    }
}

export const PricelistItemListView = {
    ...listView,
    Controller: PricelistItemListController,
};

registry.category("views").add("pricelist_item_list_modal", PricelistItemListView);